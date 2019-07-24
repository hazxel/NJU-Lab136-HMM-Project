import fiji.plugin.trackmate as trackmate
import fiji.plugin.trackmate.detection
import fiji.plugin.trackmate.tracking
import fiji.plugin.trackmate.tracking.sparselap
import fiji.plugin.trackmate.features
import fiji.plugin.trackmate.features.track
import fiji.plugin.trackmate.visualization.hyperstack
import fiji.plugin.trackmate.io.TmXmlWriter
import ij

import java.awt
import java.io

import os
import sys
import time

import logging

import re



def openImage(filename):
  filenames = {"{}{}".format(fileInfo.directory.replace("\\", "/"), fileInfo.fileName): imp for i in range(ij.WindowManager.getImageCount()) for imp in [ij.WindowManager.getImage(i + 1)] for fileInfo in [imp.getOriginalFileInfo()]}
  logging.debug("imageFilenames: {}".format(filenames))
  if filename not in filenames:
    imp = ij.IJ.openImage(filename)
    imp.show()
    filenames[filename] = imp
  return filenames[filename]


def main():
  inputPath = "X:/AchivedWorkbyName/LuSheng/MitoMoveData/tif"
  outputPath = "X:/AchivedWorkbyName/ChenXudong/MitochondrialTransport/MitoMoveData/trajectory"
  pattern = r"^(.*Div7MitoMove.*)\.tif$"
  repl = r"\1.xml"
  filenames = [("{}/{}".format(dirpath, filename), "{}/{}".format(outputPath, re.sub(pattern, repl, filename))) for dirpath, _, filenames in os.walk(inputPath) for filename in filenames if len(re.findall(pattern, filename)) > 0]
  logging.debug("filenames: {}".format(filenames))

  for inputFilename, outputFilename in filenames:
    logging.info("{} -> {}".format(inputFilename, outputFilename))

    # Get currently selected image
    imp = openImage(inputFilename)
    filename = imp.getOriginalFileInfo().fileName


    # Create the trackmate object
    settings = trackmate.Settings()
    settings.setFrom(imp)
    tm = trackmate.TrackMate(settings)

    # Configure displayer
    displayer = trackmate.visualization.hyperstack.HyperStackDisplayer(tm.getModel(), trackmate.SelectionModel(tm.getModel()), imp)
    displayerSettings = {
      "Color": java.awt.Color(1.0, 0, 1.0, 1.0),
    }
    for key, value in displayerSettings.items():
      displayer.setDisplaySettings(key, value)


    # Configure detector
    settings.detectorFactory = trackmate.detection.DogDetectorFactory()
    settings.detectorSettings = {
      "TARGET_CHANNEL": 1,
      "RADIUS": 1.05 / 2,
      "THRESHOLD": 40.0,
      "DO_MEDIAN_FILTERING": False,
      "DO_SUBPIXEL_LOCALIZATION": True,
    }
    if not tm.execDetection():
      return
    logging.info("{} detection".format(filename))

    # Configure initial spot filter
    #settings.initialSpotFilterValue = 0.0
    if not tm.execInitialSpotFiltering():
      return
    logging.info("{} initial spot filtering".format(filename))

    # Compute spot features
    if not tm.computeSpotFeatures(True):
      return
    logging.info("{} spot features".format(filename))
    displayer.render()

    # Configure spot filters
    spotFilterSettings = {
      # "QUALITY": (50, None),
      "POSITION_Z": (0.3, 3.0),
    }
    for key, (lowerBound, upperBound) in spotFilterSettings.items():
      if lowerBound is not None:
        settings.addSpotFilter(trackmate.features.FeatureFilter(key, lowerBound, True))
      if upperBound is not None:
        settings.addSpotFilter(trackmate.features.FeatureFilter(key, upperBound, False))
    if not tm.execSpotFiltering(True):
      return
    logging.info("{} spot filtering".format(filename))
    displayer.render()


    # Configure tracker
    settings.trackerFactory = trackmate.tracking.sparselap.SparseLAPTrackerFactory()
    settings.trackerSettings = {
      "ALTERNATIVE_LINKING_COST_FACTOR": 1.05,
      "BLOCKING_VALUE": float("inf"),
      "CUTOFF_PERCENTILE": 0.9,

      # Frame to frame linking
      "LINKING_MAX_DISTANCE": 2.1,
      "LINKING_FEATURE_PENALTIES": {
        "POSITION_X": 0.1,
        "POSITION_Y": 0.2,
        "POSITION_Z": 0.2,
      },

      # Track segment gap closing
      "ALLOW_GAP_CLOSING": True,
      "GAP_CLOSING_MAX_DISTANCE": 2.1,
      "MAX_FRAME_GAP": 2,
      "GAP_CLOSING_FEATURE_PENALTIES": {
        "POSITION_X": 0.2,
        "POSITION_Y": 0.4,
        "POSITION_Z": 0.4,
        "FRAME": 0.8,
      },

      # Track segment splitting
      "ALLOW_TRACK_SPLITTING": False,
      "SPLITTING_MAX_DISTANCE": 15.0,
      "SPLITTING_FEATURE_PENALTIES": {},

      # Track segment merging
      "ALLOW_TRACK_MERGING": False,
      "MERGING_MAX_DISTANCE": 15.0,
      "MERGING_FEATURE_PENALTIES": {},
    }
    if not tm.execTracking():
      return
    logging.info("{} tracking".format(filename))
    displayer.render()

    # Configure track analyzers
    settings.addTrackAnalyzer(trackmate.features.track.TrackDurationAnalyzer())
    if not tm.computeTrackFeatures(True):
      return
    logging.info("{} track features".format(filename))

    # Configure track filters
    trackFilterSettings = {
      "NUMBER_SPOTS": (9.5, None),
    }
    for key, (lowerBound, upperBound) in trackFilterSettings.items():
      if lowerBound is not None:
        settings.addTrackFilter(trackmate.features.FeatureFilter(key, lowerBound, True))
      if upperBound is not None:
        settings.addTrackFilter(trackmate.features.FeatureFilter(key, upperBound, False))
    if not tm.execTrackFiltering(True):
      return
    logging.info("{} track filtering".format(filename))
    displayer.render()

    if not tm.computeEdgeFeatures(True):
      return
    logging.info("{} edge features".format(filename))
    displayer.render()


    # Export tracks
    outputFile = java.io.File(outputFilename)
    writer = trackmate.io.TmXmlWriter(outputFile)
    writer.appendModel(tm.getModel())
    writer.appendSettings(settings)
    writer.writeToFile()
    logging.info("{} export tracks to xml".format(filename))

    imp.changes = False
    imp.close()



if __name__ == "__builtin__":
  logging.basicConfig(level=logging.INFO, format="%(asctime)s.%(msecs)03d %(levelname)8s %(filename)s:%(lineno)3s - %(msg)s", datefmt="%Y-%m-%d %H:%M:%S")
  main()
