# -*- coding: utf-8 -*-
#import math

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *


class DrawPoly(QgsMapTool):
	def __init__(self, canvas):
		QgsMapTool.__init__(self,canvas)
		self.canvas = canvas
		self.rb = QgsRubberBand(self.canvas, QGis.Polygon)

		self.cursor = QCursor(QPixmap(["16 16 3 1",
										"      c None",
										".     c #FF0000",
										"+     c #FFFFFF",
										"                ",
										"       +.+      ",
										"      ++.++     ",
										"     +.....+    ",
										"    +.     .+   ",
										"   +.   .   .+  ",
										"  +.    .    .+ ",
										" ++.    .    .++",
										" ... ...+... ...",
										" ++.    .    .++",
										"  +.    .    .+ ",
										"   +.   .   .+  ",
										"   ++.     .+   ",
										"    ++.....+    ",
										"      ++.++     ",
										"       +.+      "]))
		

	def isZoomTool(self):
		return False

	def isTransient(self):
		return False

	def isEditTool(self):
		return False

	def canvasPressEvent(self, event):
		#print 'DrawPoly : canvasPressEvent'

		if event.button() == Qt.LeftButton:
			
			point = self.canvas.getCoordinateTransform().toMapCoordinates(event.pos().x(), event.pos().y());
			self.rb.addPoint(point)
			
		else:
			if self.rb.numberOfVertices() > 2:
				self.drawDone = True
				points_xy = ''
				pt_first = str(self.rb.getPoint(0, 0).x()) + ' ' +str(self.rb.getPoint(0, 0).y())
				for i in range(self.rb.numberOfVertices()):
					points_xy += str(self.rb.getPoint(0, i).x()) + ' '
					points_xy += str(self.rb.getPoint(0, i).y()) + ','
				points_xy += pt_first
				#print points_xy
				self.drawDone = True
				#self.activate()
				self.emit(SIGNAL('drawdown'), points_xy)
			else:
				self.activate()

	def canvasMoveEvent(self,event):
		if self.drawDone:
			return

		point = self.canvas.getCoordinateTransform().toMapCoordinates(event.pos().x(),event.pos().y())
		self.rb.movePoint(point)

	def canvasReleaseEvent(self,event):
		pass

	def activate(self):
		#print 'DrawPoly : activate'
		self.drawDone = False
		self.canvas.setCursor(self.cursor)
		self.rb.reset(QGis.Polygon)
		color = QColor(255, 0, 0, 100)
		self.rb.setColor(color)
		self.rb.setWidth(1)
		
	def deactivate(self):
		#print 'DrawPoly : deactivate'
		
		if self.rb.numberOfVertices():
			self.rb.reset()
		