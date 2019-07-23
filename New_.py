from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate

from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.detection import DogDetectorFactory
from fiji.plugin.trackmate.tracking.sparselap import SparseLAPTrackerFactory
from fiji.plugin.trackmate.tracking import LAPUtils
from ij import IJ
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
import sys
import fiji.plugin.trackmate.features.track.TrackDurationAnalyzer as TrackDurationAnalyzer

from java.io import File
from fiji.plugin.trackmate.io import TmXmlWriter

import os



fileDir = 'C:/Users/stevenzhou/Desktop'

data = []

for root, dirs, files in os.walk(fileDir):
	for file in files:
		if os.path.splitext(file)[1] == '.tif':
			i = root + '/' + file
			# Output will be in the same directory
			o = root + '/' + os.path.splitext(file)[0] + '.xml'
			data.append([i, o])


for inputFile,outputFile in data:


	# Get currently selected image
	#imp = WindowManager.getCurrentImage()
	imp = IJ.openImage(inputFile)
	#imp.show()
	
	    
	#----------------------------
	# Create the model object now
	#----------------------------
	    
	# Some of the parameters we configure below need to have
	# a reference to the model at creation. So we create an
	# empty model now.
	    
	model = Model()
	    
	# Send all messages to ImageJ log window.
	model.setLogger(Logger.IJ_LOGGER)
	    
	       
	#------------------------
	# Prepare settings object
	#------------------------
	       
	settings = Settings()
	settings.setFrom(imp)
	       
	# Configure detector - We use the Strings for the keys
	settings.detectorFactory = DogDetectorFactory()
	settings.detectorSettings = { 
	    'DO_SUBPIXEL_LOCALIZATION' : True,
	    'RADIUS' : 0.6,
	    'TARGET_CHANNEL' : 1,
	    'THRESHOLD' : 50.0,
	    'DO_MEDIAN_FILTERING' : False,
	}  
	    
	# Configure spot filters - Classical filter on quality
	filter1 = FeatureFilter('QUALITY', 50, True)
	settings.addSpotFilter(filter1)
	
	filter2 = FeatureFilter('POSITION_Z', 0.3, True)
	settings.addSpotFilter(filter2)
	
	filter3 = FeatureFilter('POSITION_Z', 3.0, False)
	settings.addSpotFilter(filter3)
	
	
	# Configure tracker - We want to allow merges and fusions
	settings.trackerFactory = SparseLAPTrackerFactory()
	settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap() # almost good enough
	
	# Frame to frame linking
	settings.trackerSettings['LINKING_MAX_DISTANCE'] = 2.0
	settings.trackerSettings['LINKING_FEATURE_PENALTIES'] = {'POSITION_Y': 8.0}
	# Track segment gap closing
	settings.trackerSettings['ALLOW_GAP_CLOSING'] = True
	settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = 4.0
	settings.trackerSettings['MAX_FRAME_GAP'] = 2
	settings.trackerSettings['GAP_CLOSING_FEATURE_PENALTIES'] = {'POSITION_Y': 8.0}
	# Track segment splitting
	settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = False
	# Track segment merging
	settings.trackerSettings['ALLOW_TRACK_MERGING'] = False
	
	
	
	# Configure track analyzers - Later on we want to filter out tracks 
	# based on their displacement, so we need to state that we want 
	# track displacement to be calculated. By default, out of the GUI, 
	# not features are calculated. 
	    
	# The displacement feature is provided by the TrackDurationAnalyzer.
	    
	settings.addTrackAnalyzer(TrackDurationAnalyzer())
	    
	# Configure track filters - We want to get rid of the two immobile spots at 
	# the bottom right of the image. Track displacement must be above 10 pixels.
	    
	filter4 = FeatureFilter('NUMBER_SPOTS', 9.03, True)
	settings.addTrackFilter(filter4)
	    
	    
	#-------------------
	# Instantiate plugin
	#-------------------
	    
	trackmate = TrackMate(model, settings)
	       
	#--------
	# Process
	#--------
	    
	ok = trackmate.checkInput()
	if not ok:
	    sys.exit(str(trackmate.getErrorMessage()))
	    
	ok = trackmate.process()
	if not ok:
	    sys.exit(str(trackmate.getErrorMessage()))
	    
	       
	#----------------
	# Display results
	#----------------
	'''     
	selectionModel = SelectionModel(model)
	displayer =  HyperStackDisplayer(model, selectionModel, imp)
	displayer.render()
	displayer.refresh()
	    
	# Echo results with the logger we set at start:
	model.getLogger().log(str(model))
	'''
	
	outputFile = File(outputFile)
	writer = TmXmlWriter(outputFile)
	writer.appendModel(model)
	writer.writeToFile()