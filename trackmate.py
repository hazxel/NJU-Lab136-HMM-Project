#!/usr/bin/env python3

import os

import logging

import argparse
import bs4
import scipy.io



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
def initial():
  # os.environ.update(zip(("LINES", "COLUMNS"), os.popen('stty size', 'r').read().split()))
  for no, c in [(logging.CRITICAL, color.magenta), (logging.ERROR, color.red), (logging.WARNING, color.yellow), (logging.INFO, color.green), (logging.DEBUG, color.white)]:
    logging.addLevelName(no, c(logging.getLevelName(no)))



def trackmate(filename, **kargs):
  with open(filename, encoding="utf-8") as f:
    soup = bs4.BeautifulSoup(f.read(), features="xml")

  tracks = soup.Tracks("particle")
  trajectorys = []
  for track in tracks:
    particles = []
    tPrev = int(track.detection["t"]) - 1
    for particle in track("detection"):
      xCurrent, tCurrent = float(particle["x"]), int(particle["t"])
      particles.extend([(t - tPrev) * (xCurrent - particles[-1]) / (tCurrent - tPrev) + particles[-1] for t in range(tPrev + 1, tCurrent)])
      particles.append(xCurrent)
      tPrev = tCurrent

    particles = list(map(float.__sub__, particles[1:], particles[:-1]))
    trajectorys.append(particles)

  logging.info(f"keep {len(trajectorys)} out of {len(tracks)} trajectories")

  # import pdb; pdb.set_trace()
  if kargs["mat"] is not None:
    scipy.io.savemat(kargs["mat"], {"T": trajectorys})



def main():
  parser = argparse.ArgumentParser(description="Extract tracks from trackmate xml")
  parser.add_argument("-V", "--version", action="version", version="%(prog)s 0.1")
  parser.add_argument("-v", "--verbose", help=f"set log level to {logging.getLevelName(30)}, {logging.getLevelName(20)} or {logging.getLevelName(10)} (default {logging.getLevelName(40)})", action="count", default=0)

  parser.add_argument("filename", help="xml filename")
  parser.add_argument("--mat", help="save to FILENAME as mat", metavar="FILENAME")

  args = parser.parse_args()

  logging.basicConfig(level=max(0, logging.ERROR - args.verbose * 10), format="%(asctime)s.%(msecs)03d %(levelname)19s %(filename)s:%(lineno)3s - %(msg)s", datefmt="%Y-%m-%d %H:%M:%S")
  logging.info(f"Arguments: {args}")

  trackmate(**args.__dict__)



if __name__ == "__main__":
  initial()
  main()
