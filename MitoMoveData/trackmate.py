#!/usr/bin/env python3

import os
import platform

import logging

import argparse
import bs4
import scipy.io

import networkx as nx
import re



class color:
  _colors = dict(zip(["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"], range(8)))
  def __init__(self, bold=True, fg=None, bg=None):
    self._bold, self._fg, self._bg = bold, fg, bg
  def __getattr__(self, c):
    if c.lower() == "default":
      return __class__()
    if c.lower() == "bold":
      return __class__(not self._bold, self._fg, self._bg)
    if c.lower() in self._colors:
      return __class__(self._bold, **dict({"fg": self._fg, "bg": self._bg}, **{"fg" if c == c.lower() else "bg": self._colors[c.lower()]}))
    if c.lower() == "light":
      g = self._fg if c == c.lower() else self._bg
      if g is not None and g < 16:
        return __class__(self._bold, **dict({"fg": self._fg, "bg": self._bg}, **{"fg" if c == c.lower() else "bg": g + 8 if g < 8 else g - 8}))
      raise KeyError("not system color can not be light")
    if c.lower() == "gray":
      def gray(i):
        if 0 <= i < 26:
          return __class__(self._bold, **dict({"fg": self._fg, "bg": self._bg}, **{"fg" if c == c.lower() else "bg": 16 if i == 0 else i + 231 if i < 25 else 231}))
        raise KeyError("gray should be in [0, 26)")
      return gray
    if c.lower() == "rgb":
      def rgb(r, g, b):
        if 0 <= r < 6 and 0 <= g < 6 and 0 <= b < 6:
          return __class__(self._bold, **dict({"fg": self._fg, "bg": self._bg}, **{"fg" if c == c.lower() else "bg": r * 36 + g * 6 + b + 16}))
        raise KeyError("rgb should be in [0, 6)")
      return rgb
    raise KeyError("color is not correct")
  __getitem__ = __getattr__
  def __call__(self, s=""):
    fg = "" if self._fg is None else f';{self._fg + 30}' if self._fg < 8 else f';{self._fg + 82}' if self._fg < 16 else f';38;5;{self._fg:>03}'
    bg = "" if self._bg is None else f';{self._bg + 40}' if self._bg < 8 else f';{self._bg + 92}' if self._bg < 16 else f';48;5;{self._bg:>03}'
    return "" if s == "" else f'\033[{"1" if self._bold else "0"}{fg}{bg}m{s}\033[0m'
color = color()



def getAllSpotsDict(allSpots):
    spotsDict = {}
    for spot in allSpots("Spot"):
        spotsDict[int(spot["ID"])] = {
            "VISIBILITY" : int(spot["VISIBILITY"]),
            "RADIUS" : float(spot["RADIUS"]),
            "QUALITY" : float(spot["QUALITY"]),
            "T" : int(float(spot["POSITION_T"])),
            "X" : float(spot["POSITION_X"]),
            "Y" : float(spot["POSITION_Y"]),
            "Z" : float(spot["POSITION_Z"]),
            "FRAME" : int(spot["FRAME"]),
        }
    return spotsDict



def getSpotsSeq(track, allSpotsDict):
    # construct the track
    directedGraph = nx.DiGraph()
    for edge in track("Edge"):
        source, target = int(edge["SPOT_SOURCE_ID"]), int(edge["SPOT_TARGET_ID"])
        directedGraph.add_edge(source, target)

    # find out the root by dfs
    reversedGraph = directedGraph.reverse()
    arbitraryNode = list(reversedGraph.nodes)[0]
    arbitraryPath = list(nx.dfs_postorder_nodes(reversedGraph, source = arbitraryNode))
    root = arbitraryPath[0]

    spotsSeq = list(nx.dfs_preorder_nodes(directedGraph, source = root))
    return spotsSeq




def trackmate(path, pattern, **kargs):
  filenames = ["{}/{}".format(dirpath, filename) for dirpath, _, filenames in os.walk(path) for filename in filenames if len(re.findall(pattern, filename)) > 0]
  logging.debug(f"filenames: {filenames}")

  ans = []
  for filename in filenames:
    logging.info(filename)

    with open(filename, encoding="utf-8") as f:
      soup = bs4.BeautifulSoup(f.read(), features="xml")

    allSpotsDict = getAllSpotsDict(soup.AllSpots)
    allTracks = soup.AllTracks("Track")

    trajectorys = []
    for track in allTracks:
      if len(track("Edge")) < kargs["nspots"]:
        continue

      spotsSeq = getSpotsSeq(track, allSpotsDict)
      Positions_X = []
      tPrev = allSpotsDict[spotsSeq[0]]["T"] - 1
      for spotID in spotsSeq:
        xCurrent, tCurrent = allSpotsDict[int(spotID)]["X"], allSpotsDict[int(spotID)]["T"]
        Positions_X.extend([(t - tPrev) * (xCurrent - Positions_X[-1]) / (tCurrent - tPrev) + Positions_X[-1] for t in range(tPrev + 1, tCurrent)])
        Positions_X.append(xCurrent)
        tPrev = tCurrent
      Positions_X = list(map(float.__sub__, Positions_X[1:], Positions_X[:-1]))
      trajectorys.append(Positions_X)
    logging.info(f"keep {len(trajectorys)} out of {len(allTracks)} trajectories")

    ans.extend(trajectorys)

  outputPath, _ = os.path.split(kargs["mat"])
  if not os.path.exists(outputPath):
    os.mkdir(outputPath, mode=0o755)
  if kargs["mat"] is not None:
    scipy.io.savemat(kargs["mat"], {"T": ans})



def main():
  parser = argparse.ArgumentParser(description="Extract tracks from trackmate xml")
  parser.add_argument("-V", "--version", action="version", version="%(prog)s 0.1")
  parser.add_argument("-v", "--verbose", help=f"set log level to {logging.getLevelName(30)}, {logging.getLevelName(20)} or {logging.getLevelName(10)} (default {logging.getLevelName(40)})", action="count", default=0)

  parser.add_argument("path", help="xml input path")
  parser.add_argument("pattern", help="xml filename pattern")
  parser.add_argument("--mat", help="save to FILENAME as mat", metavar="FILENAME")
  parser.add_argument("--nspots", help="number of spots per trajectory at least", type=int, default=0)

  args = parser.parse_args()

  logging.basicConfig(level=max(0, logging.ERROR - args.verbose * 10), format="%(asctime)s.%(msecs)03d %(levelname)19s %(filename)s:%(lineno)3s - %(msg)s", datefmt="%Y-%m-%d %H:%M:%S")
  logging.info(f"Arguments: {args}")

  trackmate(**args.__dict__)



if __name__ == "__main__":
  if platform.system() == "Linux":
    os.environ.update(zip(("LINES", "COLUMNS"), os.popen('stty size', 'r').read().split()))
    for no, c in [(logging.CRITICAL, color.magenta), (logging.ERROR, color.red), (logging.WARNING, color.yellow), (logging.INFO, color.green), (logging.DEBUG, color.white)]:
      logging.addLevelName(no, c(logging.getLevelName(no)))
  main()
