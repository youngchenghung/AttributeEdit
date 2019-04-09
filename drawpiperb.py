# -*- coding: utf-8 -*-
import math

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from qgis.core import *
from qgis.gui import *

class DrawPipeRB(QgsMapTool):
	def __init__(self, canvas):
		QgsMapTool.__init__(self, canvas)
		
		self.rb = QgsRubberBand(self.canvas())
		self.rb.setIcon(QgsRubberBand.ICON_CIRCLE)
		self.rb.setColor(QColor(0, 0, 255, 200))
		self.rb.setWidth(2)
		self.rb.setVisible(False)

		self.draw_done = False
		self.frame_no = u''
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

	def activate(self):
		self.canvas().setCursor(self.cursor)
		self.rb.reset()
		self.draw_done = False
		self.frame_no = u''

	def deactivate(self):
		#print 'deactivate'
		if self.rb.numberOfVertices():
			self.rb.reset()
		#QgsMapTool.deactivate(self)

	def canvasPressEvent(self, event):
		#print 'canvasPressEvent'
		

		if event.button() == Qt.LeftButton:
			if self.rb.numberOfVertices() == 0:

				point = self.toMapCoordinates(event.pos())
				#print 'point : ', point.toString()
				point_xy = unicode(point.x()) + u' ' + unicode(point.y())
				query_string = u'SELECT no FROM frame WHERE ST_Contains(the_geom, ST_GeometryFromText(\'POINT({})\', 4326))'.format(point_xy)
				#print query_string
				db_conn = self.get_db_connection()
				query = db_conn.exec_(query_string)
				
				if query.isActive():
					# 判斷是否有點在圖框中
					if query.size() > 0:
						while query.next():
							self.frame_no = query.value(0)
							#print self.frame_no
					else:
						self.emit(SIGNAL("drawdown"), False)
				else:
					self.emit(SIGNAL("drawdown"), u'SQL Error')
				
				query.clear()
				db_conn.close()

	def canvasReleaseEvent(self, event):

		if event.button() == Qt.LeftButton:
			if len(self.frame_no) > 0:
				point = self.toMapCoordinates(event.pos())
				self.rb.addPoint(point)
		elif event.button() == Qt.RightButton:
			if self.rb.numberOfVertices() > 1:
				self.draw_done = True
				self.emit(SIGNAL("drawdown"), self.rb.asGeometry(), self.frame_no)
		else:
			return

		#print 'self.rb.numberOfVertices() : ', self.rb.numberOfVertices()

	def canvasMoveEvent(self, event):
		if self.draw_done:
			return

		point = self.toMapCoordinates(event.pos())
		self.rb.movePoint(point)

	# 開啟與 資料庫 的連線
	def get_db_connection(self):
		# 取得現有 QGIS 圖層之資料來源
		#layer = self.iface.activeLayer()
		layer = self.canvas().layer(0)
		provider = layer.dataProvider()
		# 若目前有圖層開啟的狀態，則取得圖層的連接資訊
		if provider.name() == 'postgres':
			# get the URI containing the connection parameters
			uri = QgsDataSourceURI(provider.dataSourceUri())
			pg_conn = QSqlDatabase.addDatabase('QPSQL')
			if pg_conn.isValid():
				pg_conn.setHostName(uri.host())
				pg_conn.setDatabaseName(uri.database())
				pg_conn.setPort(int(uri.port()))
				pg_conn.setUserName(uri.username())
				pg_conn.setPassword(uri.password())
				
			if not pg_conn.open():
				err = pg_conn.lastError()
				print err.driverText()
			else:
				return pg_conn


class DrawPipeSnap(QgsMapTool):
	def __init__(self, canvas):
		QgsMapTool.__init__(self, canvas)
		self.rb = QgsRubberBand(self.canvas())
		self.rb.setIcon(QgsRubberBand.ICON_CIRCLE)
		self.rb.setColor(QColor(0, 0, 255, 200))
		self.rb.setWidth(2)
		self.rb.setVisible(False)

		self.vertex_band = QgsRubberBand(self.canvas())
		self.vertex_band.setIcon(QgsRubberBand.ICON_CIRCLE)
		self.vertex_band.setColor(Qt.magenta)
		self.vertex_band.setIconSize(5)
		self.vertex_band.setVisible(False)

		self.edge_band = QgsRubberBand(self.canvas())
		color = QColor(Qt.magenta)
		color.setAlpha(color.alpha()/5)
		self.edge_band.setColor(color)
		self.edge_band.setWidth(5)
		self.edge_band.setVisible(False)

		self.draw_done = False
		self.frame_no = u''
		
	def activate(self):
		#self.canvas().setCursor(self.cursor)
		#self.cursor = QCursor().setShape(Qt.ArrowCursor)
		cursor = QCursor(Qt.ArrowCursor)
		self.canvas().setCursor(cursor)
		self.rb.reset()
		self.draw_done = False
		self.frame_no = u''

	def deactivate(self):
		if self.vertex_band.numberOfVertices():
			self.vertex_band.reset()
		
		if self.rb.numberOfVertices():
			self.rb.reset()
		#QgsMapTool.deactivate(self)

	def canvasPressEvent(self, event):
		#print 'canvasPressEvent'
		
		if event.button() == Qt.LeftButton:
			if self.rb.numberOfVertices() == 0:

				point = self.toMapCoordinates(event.pos())
				#print 'point : ', point.toString()
				point_xy = unicode(point.x()) + u' ' + unicode(point.y())
				query_string = u'SELECT no FROM frame WHERE ST_Contains(the_geom, ST_GeometryFromText(\'POINT({})\', 4326))'.format(point_xy)
				#print query_string
				db_conn = self.get_db_connection()
				query = db_conn.exec_(query_string)
				
				if query.isActive():
					# 判斷是否有點在圖框中
					if query.size() > 0:
						while query.next():
							self.frame_no = query.value(0)
							#print self.frame_no
					else:
						self.emit(SIGNAL("drawdown"), False)
				else:
					self.emit(SIGNAL("drawdown"), u'SQL Error')
				
				query.clear()
				db_conn.close()

	def canvasReleaseEvent(self, event):
		# 滑鼠左鍵觸發
		if event.button() == Qt.LeftButton:
			if len(self.frame_no) > 0:
				point = self.toMapCoordinates(event.pos())
				tol = 10.0
				snap_type = QgsPointLocator.Type(QgsPointLocator.Vertex|QgsPointLocator.Edge)

				for layer in self.canvas().layers():
					if layer.name() == u'pipe':
						lyr = layer
						
				#snap_lyr = QgsSnappingUtils.LayerConfig(lyr, QgsPointLocator.Vertex, 10.0, QgsTolerance.Pixels)
				snap_lyr = QgsSnappingUtils.LayerConfig(lyr, snap_type, tol, QgsTolerance.Pixels)
				snap_util = self.canvas().snappingUtils()
				snap_util.setLayers([snap_lyr])
				snap_util.setSnapToMapMode(QgsSnappingUtils.SnapAdvanced)
				snap_util.setSnapOnIntersections(False)  # only snap to layers
				m = snap_util.snapToMap(point)

				if m.type() == QgsPointLocator.Vertex:
					#self.rb.addPoint(point)
					self.rb.addPoint(m.point())
				elif m.type() == QgsPointLocator.Edge:
					#print 'point : ', point.toString()
					#print 'm : ', m.point().toString()
					self.rb.addPoint(m.point())
				else:
					self.rb.addPoint(point)

		# 滑鼠右鍵觸發
		elif event.button() == Qt.RightButton:
			if self.rb.numberOfVertices() > 1:
				if self.vertex_band.numberOfVertices():
					self.vertex_band.reset()

				self.draw_done = True
				self.emit(SIGNAL("drawdown"), self.rb.asGeometry(), self.frame_no)
		else:
			return

		#print 'self.rb.numberOfVertices() : ', self.rb.numberOfVertices()

	def canvasMoveEvent(self, event):
		if self.draw_done:
			return

		point = self.toMapCoordinates(event.pos())
		tol = 10.0
		snap_type = QgsPointLocator.Type(QgsPointLocator.Vertex|QgsPointLocator.Edge)

		for layer in self.canvas().layers():
				if layer.name() == u'pipe':
					lyr = layer

		#snap_lyr = QgsSnappingUtils.LayerConfig(lyr, QgsPointLocator.Vertex, 10.0, QgsTolerance.Pixels)
		snap_lyr = QgsSnappingUtils.LayerConfig(lyr, snap_type, tol, QgsTolerance.Pixels)
		snap_util = self.canvas().snappingUtils()
		snap_util.setLayers([snap_lyr])
		snap_util.setSnapToMapMode(QgsSnappingUtils.SnapAdvanced)
		snap_util.setSnapOnIntersections(False)  # only snap to layers
		m = snap_util.snapToMap(point)

		if m.type() == QgsPointLocator.Vertex:
			self.vertex_band.setToGeometry(QgsGeometry.fromPoint(m.point()), None)
			self.vertex_band.setVisible(True)
		else:
			self.vertex_band.setVisible(False)

		if m.type() == QgsPointLocator.Edge:
			p0, p1 = m.edgePoints()
			self.edge_band.setToGeometry(QgsGeometry.fromPolyline([p0, p1]), None)
			self.edge_band.setVisible(True)
		else:
			self.edge_band.setVisible(False)

		if self.rb.numberOfVertices():
			self.rb.movePoint(point)

	# 開啟與 資料庫 的連線
	def get_db_connection(self):
		# 取得現有 QGIS 圖層之資料來源
		#layer = self.iface.activeLayer()
		layer = self.canvas().layer(0)
		provider = layer.dataProvider()
		# 若目前有圖層開啟的狀態，則取得圖層的連接資訊
		if provider.name() == 'postgres':
			# get the URI containing the connection parameters
			uri = QgsDataSourceURI(provider.dataSourceUri())
			pg_conn = QSqlDatabase.addDatabase('QPSQL')
			if pg_conn.isValid():
				pg_conn.setHostName(uri.host())
				pg_conn.setDatabaseName(uri.database())
				pg_conn.setPort(int(uri.port()))
				pg_conn.setUserName(uri.username())
				pg_conn.setPassword(uri.password())
				
			if not pg_conn.open():
				err = pg_conn.lastError()
				print err.driverText()
			else:
				return pg_conn


class DrawPipeRoad(QgsMapTool):
	def __init__(self, canvas):
		QgsMapTool.__init__(self, canvas)
		self.rb = QgsRubberBand(self.canvas())
		self.rb.setIcon(QgsRubberBand.ICON_CIRCLE)
		self.rb.setColor(QColor(0, 0, 255, 200))
		self.rb.setWidth(2)
		self.rb.setVisible(False)

		self.vertex_band = QgsRubberBand(self.canvas())
		self.vertex_band.setIcon(QgsRubberBand.ICON_CIRCLE)
		self.vertex_band.setColor(Qt.magenta)
		self.vertex_band.setIconSize(3)
		self.vertex_band.setVisible(False)

		self.edge_band = QgsRubberBand(self.canvas())
		color = QColor(Qt.magenta)
		color.setAlpha(color.alpha()/5)
		self.edge_band.setColor(color)
		self.edge_band.setWidth(5)
		self.edge_band.setVisible(False)

		self.draw_done = False
		self.frame_no = u''
		

	def activate(self):
		#self.canvas().setCursor(self.cursor)
		cursor = QCursor(Qt.ArrowCursor)
		self.canvas().setCursor(cursor)
		self.rb.reset()
		self.draw_done = False
		self.frame_no = u''

	def deactivate(self):
		if self.vertex_band.numberOfVertices():
			self.vertex_band.reset()
		
		if self.rb.numberOfVertices():
			self.rb.reset()
		#QgsMapTool.deactivate(self)

	def canvasPressEvent(self, event):
		#print 'canvasPressEvent'
		
		if event.button() == Qt.LeftButton:
			if self.rb.numberOfVertices() == 0:

				point = self.toMapCoordinates(event.pos())
				#print 'point : ', point.toString()
				point_xy = unicode(point.x()) + u' ' + unicode(point.y())
				query_string = u'SELECT no FROM frame WHERE ST_Contains(the_geom, ST_GeometryFromText(\'POINT({})\', 4326))'.format(point_xy)
				#print query_string
				db_conn = self.get_db_connection()
				query = db_conn.exec_(query_string)
				
				if query.isActive():
					# 判斷是否有點在圖框中
					if query.size() > 0:
						while query.next():
							self.frame_no = query.value(0)
							#print self.frame_no
					else:
						self.emit(SIGNAL("drawdown"), False)
				else:
					self.emit(SIGNAL("drawdown"), u'SQL Error')
				
				query.clear()
				db_conn.close()

	def canvasReleaseEvent(self, event):
		# 滑鼠左鍵觸發
		if event.button() == Qt.LeftButton:
			if len(self.frame_no) > 0:
				point = self.toMapCoordinates(event.pos())
				#snap_type = QgsPointLocator.Type(QgsPointLocator.Vertex|QgsPointLocator.Edge)
				snap_type = QgsPointLocator.Type(QgsPointLocator.Vertex)
				tol = 10.0
				for layer in self.canvas().layers():
					if layer.name() == u'rodes':
						lyr = layer

				#snap_lyr = QgsSnappingUtils.LayerConfig(lyr, QgsPointLocator.Vertex, 10, QgsTolerance.Pixels)
				snap_lyr = QgsSnappingUtils.LayerConfig(lyr, snap_type, tol, QgsTolerance.Pixels)
				snap_util = self.canvas().snappingUtils()
				snap_util.setLayers([snap_lyr])
				snap_util.setSnapToMapMode(QgsSnappingUtils.SnapAdvanced)
				snap_util.setSnapOnIntersections(False)  # only snap to layers
				m = snap_util.snapToMap(point)

				if m.type() == QgsPointLocator.Vertex:
					self.rb.addPoint(m.point())
				elif m.type() == QgsPointLocator.Edge:
					self.rb.addPoint(m.point())
				else:
					self.rb.addPoint(point)

		# 滑鼠右鍵觸發
		elif event.button() == Qt.RightButton:
			if self.rb.numberOfVertices() > 1:
				if self.vertex_band.numberOfVertices():
					self.vertex_band.reset()

				self.draw_done = True
				self.emit(SIGNAL("drawdown"), self.rb.asGeometry(), self.frame_no)
		else:
			return

		#print 'self.rb.numberOfVertices() : ', self.rb.numberOfVertices()

	def canvasMoveEvent(self, event):
		if self.draw_done:
			return

		point = self.toMapCoordinates(event.pos())
		snap_type = QgsPointLocator.Type(QgsPointLocator.Vertex|QgsPointLocator.Edge)
		tol = 10.0

		for layer in self.canvas().layers():
				if layer.name() == u'rodes':
					lyr = layer

		#snap_lyr = QgsSnappingUtils.LayerConfig(lyr, QgsPointLocator.Vertex, 10, QgsTolerance.Pixels)
		snap_lyr = QgsSnappingUtils.LayerConfig(lyr, snap_type, tol, QgsTolerance.Pixels)
		snap_util = self.canvas().snappingUtils()
		snap_util.setLayers([snap_lyr])
		snap_util.setSnapToMapMode(QgsSnappingUtils.SnapAdvanced)
		snap_util.setSnapOnIntersections(False)  # only snap to layers
		m = snap_util.snapToMap(point)

		if m.type() == QgsPointLocator.Vertex:
			self.vertex_band.setToGeometry(QgsGeometry.fromPoint(m.point()), None)
			self.vertex_band.setVisible(True)
		else:
			self.vertex_band.setVisible(False)

		if m.type() == QgsPointLocator.Edge:
			p0, p1 = m.edgePoints()
			self.edge_band.setToGeometry(QgsGeometry.fromPolyline([p0, p1]), None)
			self.edge_band.setVisible(True)
		else:
			self.edge_band.setVisible(False)

		if self.rb.numberOfVertices():
			self.rb.movePoint(point)

	# 開啟與 資料庫 的連線
	def get_db_connection(self):
		# 取得現有 QGIS 圖層之資料來源
		#layer = self.iface.activeLayer()
		layer = self.canvas().layer(0)
		provider = layer.dataProvider()
		# 若目前有圖層開啟的狀態，則取得圖層的連接資訊
		if provider.name() == 'postgres':
			# get the URI containing the connection parameters
			uri = QgsDataSourceURI(provider.dataSourceUri())
			pg_conn = QSqlDatabase.addDatabase('QPSQL')
			if pg_conn.isValid():
				pg_conn.setHostName(uri.host())
				pg_conn.setDatabaseName(uri.database())
				pg_conn.setPort(int(uri.port()))
				pg_conn.setUserName(uri.username())
				pg_conn.setPassword(uri.password())
				
			if not pg_conn.open():
				err = pg_conn.lastError()
				print err.driverText()
			else:
				return pg_conn