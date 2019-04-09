# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
#from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *


class IdentifyEquipTool(QgsMapToolIdentify):

	def __init__(self, canvas):
		QgsMapToolIdentify.__init__(self, canvas)

	def canvasReleaseEvent(self, mouseEvent):
		#print QgsMapLayerRegistry.instance().mapLayers()
		layer_name = ['eumeter', 'meter', 'station', 'pcross', 'pipecover', 'pipehat']
		
		# get features at the current mouse position
		# enum QgsMapToolIdentify::IdentifyMode
		# DefaultQgsSetting, ActiveLayer ,TopDownStopAtFirst ,TopDownAll ,LayerSelection 
		# enum QgsMapToolIdentify::Type
		# VectorLayer, RasterLayer, AllLayers 	
		results = self.identify(mouseEvent.x(), mouseEvent.y(), self.TopDownAll, self.VectorLayer)
		#results = self.identify(mouseEvent.x(), mouseEvent.y(), QgsMapLayerRegistry.instance().mapLayersByName('station'), self.DefaultQgsSetting)

		if len(results) > 0:
			if results[0].mLayer.name() in layer_name:
				# signal that a feature was identified
				self.emit(SIGNAL('featureIdentified'), results[0].mLayer.name(), results[0].mFeature)

class IdentifyPipeTool(QgsMapToolIdentify):

	def __init__(self, canvas):
		QgsMapToolIdentify.__init__(self, canvas)

	def canvasReleaseEvent(self, mouseEvent):
		layer_name = ['pipe', 'pipediscard']
		
		results = self.identify(mouseEvent.x(), mouseEvent.y(), self.TopDownStopAtFirst , self.VectorLayer)

		if len(results) > 0:
			if results[0].mLayer.name() in layer_name:
				self.emit(SIGNAL('featureIdentified'), results[0].mLayer.name(), results[0].mFeature)

class IdentifyValveTool(QgsMapToolIdentify):

	def __init__(self, canvas):
		QgsMapToolIdentify.__init__(self, canvas)

	def canvasReleaseEvent(self, mouseEvent):
		layer_name = ['pipe']
		
		results = self.identify(mouseEvent.x(), mouseEvent.y(), self.TopDownStopAtFirst , self.VectorLayer)

		if len(results) > 0:
			if results[0].mLayer.name() in layer_name:
				self.emit(SIGNAL('featureIdentified'), results[0].mLayer.name(), results[0].mFeature)

class IdentifyProjdesTool(QgsMapToolIdentify):

	def __init__(self, canvas):
		QgsMapToolIdentify.__init__(self, canvas)

	def canvasReleaseEvent(self, mouseEvent):
		#print QgsMapLayerRegistry.instance().mapLayers()
		layer_name = ['pipe', 'projinf']
		
		# get features at the current mouse position
		results = self.identify(mouseEvent.x(), mouseEvent.y(), self.TopDownStopAtFirst , self.VectorLayer)
		#results = self.identify(mouseEvent.x(), mouseEvent.y(), QgsMapLayerRegistry.instance().mapLayersByName('station'), self.DefaultQgsSetting)

		if len(results) > 0:
			if results[0].mLayer.name() in layer_name:
				# signal that a feature was identified
				self.emit(SIGNAL('featureIdentified'), results[0].mLayer.name(), results[0].mFeature)

class ImgVHTool(QgsMapToolIdentify):

	def __init__(self, canvas):
		QgsMapToolIdentify.__init__(self, canvas)

	def canvasReleaseEvent(self, mouseEvent):
		#print QgsMapLayerRegistry.instance().mapLayers()
		layer_name = ['hydrant', 'valve']
		
		# get features at the current mouse position
		results = self.identify(mouseEvent.x(), mouseEvent.y(), self.TopDownStopAtFirst , self.VectorLayer)
		#results = self.identify(mouseEvent.x(), mouseEvent.y(), QgsMapLayerRegistry.instance().mapLayersByName('station'), self.DefaultQgsSetting)

		if len(results) > 0:
			if results[0].mLayer.name() in layer_name:
				# signal that a feature was identified
				self.emit(SIGNAL('featureIdentified'), results[0].mLayer.name(), results[0].mFeature)

class ImgDrawingsTool(QgsMapToolIdentify):

	def __init__(self, canvas):
		QgsMapToolIdentify.__init__(self, canvas)

	def canvasReleaseEvent(self, mouseEvent):
		#print QgsMapLayerRegistry.instance().mapLayers()
		#layer_name = ['eumeter', 'hydrant', 'manhole', 'pipe', 'station', 'valve']
		layer_name = ['eumeter', 'pipe']
		
		# get features at the current mouse position
		results = self.identify(mouseEvent.x(), mouseEvent.y(), self.TopDownStopAtFirst , self.VectorLayer)
		#results = self.identify(mouseEvent.x(), mouseEvent.y(), QgsMapLayerRegistry.instance().mapLayersByName('station'), self.DefaultQgsSetting)

		if len(results) > 0:
			if results[0].mLayer.name() in layer_name:
				# signal that a feature was identified
				self.emit(SIGNAL('featureIdentified'), results[0].mLayer.name(), results[0].mFeature)
			

class IdentifyRegionTool(QgsMapToolIdentify):

	def __init__(self, canvas):
		QgsMapToolIdentify.__init__(self, canvas)

	def canvasReleaseEvent(self, mouseEvent):
		#print QgsMapLayerRegistry.instance().mapLayers()
		layer_name = ['valve', 'manhole', 'hydrant']
		
		# get features at the current mouse position
		# enum QgsMapToolIdentify::IdentifyMode
		# DefaultQgsSetting, ActiveLayer ,TopDownStopAtFirst ,TopDownAll ,LayerSelection 
		# enum QgsMapToolIdentify::Type
		# VectorLayer, RasterLayer, AllLayers 	
		results = self.identify(mouseEvent.x(), mouseEvent.y(), self.TopDownAll, self.VectorLayer)
		#results = self.identify(mouseEvent.x(), mouseEvent.y(), QgsMapLayerRegistry.instance().mapLayersByName('station'), self.DefaultQgsSetting)

		if len(results) > 0:
			result_list = []
			for result in results:
				if result.mLayer.name() in layer_name:
					#featuers.append(result.mFeature)
					# [<qgis._gui.IdentifyResult object at 0x000000001063EEA0>, <qgis._gui.IdentifyResult object at 0x000000001063EF28>]
					result_list.append(result) 

			self.emit(SIGNAL('featureIdentified'), result_list)
					
			'''
			if results[0].mLayer.name() in layer_name:
				# signal that a feature was identified
				self.emit(SIGNAL('featureIdentified'), results[0].mLayer.name(), results[0].mFeature)
			'''

