# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AttributeEdit
                                 A QGIS plugin
 edittool
                              -------------------
        begin                : 2018-11-14
        git sha              : $Format:%H$
        copyright            : (C) 2018 by  
        email                :  
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from PyQt4.QtSql import *
from qgis.utils import *
from qgis.gui import *

import math
import os
import ConfigParser  
import sys
from xlutils.copy import copy   # http://pypi.python.org/pypi/xlutils
from xlrd import open_workbook  # http://pypi.python.org/pypi/xlrd
from xlwt import easyxf         # http://pypi.python.org/pypi/xlwt
import time
import subprocess

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from attribute_edit_dialog import PickFeaturesDialog, ValveAttributeDialog, ManholeAttributeDialog, HydrantAttributeDialog

#from identifyfeattool import IdentifyValveTool

from identifyfeattool import IdentifyRegionTool

import os.path

unitcode=""
iButton = 0
frame_no = ""
iNow_photoname = 0
nas_ip=""
nas_folder=""
filepath=""
Photopathname=""
g_gid=""
g_uid=""

class AttributeEdit:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        global unitcode
        global nas_folder,nas_ip
        self.subclass_id = u''
        self.temp_path = u'C:\\'
        self.img_path = u''
        self.img_ctrl = 1
        self.images = []
        self.featX=0
        self.featY=0
        self.tp_type=''
        self.x97 = ''
        self.y96 = ''
        self.rubberband = QgsRubberBand
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        mc = self.canvas
        self.clickTool = None
        #QgsMessageLog.logMessage("ModValveTool ini Unitcode="+unitcode, "WaterMaintain")

        self.pick_features_dlg = PickFeaturesDialog()
        self.pick_features_dlg.setWindowTitle(u'選取圖徵')

        #self.select_features_dlg = SelectFeaturesDialog()
        #self.select_features_dlg.setWindowTitle(u'選取圖徵')

        self.valve_attribute_dlg = ValveAttributeDialog()
        self.valve_attribute_dlg.setWindowTitle(u'閥屬性修改')

        self.manhole_attribute_dlg = ManholeAttributeDialog()
        self.manhole_attribute_dlg.setWindowTitle(u'人孔蓋屬性修改')

        self.hydrant_attribute_dlg = HydrantAttributeDialog()
        self.hydrant_attribute_dlg.setWindowTitle(u'消防栓屬性修改')

    def initGui(self):
        self.toolBar = self.iface.addToolBar(u'屬性修改')
        self.toolBar.setObjectName('屬性修改')

        self.action_attribute_edit = QAction(QIcon("C:/Users/tesla/.qgis2/python/plugins/AttributeEdit/icon.png"), u"屬性修改", self.iface.mainWindow())
        self.action_attribute_edit.setCheckable(True)
        #self.action_attribute_edit.triggered.connect(self.select_features)
        self.action_attribute_edit.triggered.connect(self.edit_features_tool_init)

        self.toolBar.addAction(self.action_attribute_edit)


        #self.pick_features_dlg.ui.listWidget_pick.clicked.connect(self.valve_attribute_init)
        #self.pick_features_dlg.ui.listWidget_pick.clicked.connect(self.manhole_attribute_init)
        #self.pick_features_dlg.ui.listWidget_pick.clicked.connect(self.hydrant_attribute_init)
        self.pick_features_dlg.ui.listWidget_pick.clicked.connect(self.attribute_init)

        # valve_attribute_dlg
        self.valve_attribute_dlg.ui.pushButtonOK.clicked.connect(self.edit_valve_ok)
        self.valve_attribute_dlg.ui.pushButtonCancel.clicked.connect(self.valve_attribute_close)
        self.valve_attribute_dlg.ui.cbP1pos.currentIndexChanged.connect(self.cbp1posOnChange)
        self.valve_attribute_dlg.ui.cbP2pos.currentIndexChanged.connect(self.cbp2posOnChange)
        self.valve_attribute_dlg.ui.cbP3pos.currentIndexChanged.connect(self.cbp3posOnChange)
        self.valve_attribute_dlg.ui.teP1disc.textChanged.connect(self.tep1discOnChange)
        self.valve_attribute_dlg.ui.teP2disc.textChanged.connect(self.tep2discOnChange)
        self.valve_attribute_dlg.ui.teP3disc.textChanged.connect(self.tep3discOnChange)
        self.valve_attribute_dlg.ui.teVx.setText("")
        self.valve_attribute_dlg.ui.teVy.setText("")
        self.valve_attribute_dlg.ui.btP1xy.clicked.connect(self.GetP1xy)
        self.valve_attribute_dlg.ui.btP2xy.clicked.connect(self.GetP2xy)
        self.valve_attribute_dlg.ui.btP3xy.clicked.connect(self.GetP3xy)
        self.valve_attribute_dlg.ui.pushButtonOK_valve_pin.clicked.connect(self.pin_save)
        #self.valve_attribute_dlg.ui.teP1x.textChanged.connect(self.tep1OnChange)

        #manhole_attribute_dlg
        self.manhole_attribute_dlg.ui.pushButtonOK.clicked.connect(self.edit_manhole_ok)
        self.manhole_attribute_dlg.ui.pushButtonCancel.clicked.connect(self.manhole_attribute_close)
        self.manhole_attribute_dlg.ui.cbP1pos.currentIndexChanged.connect(self.cbp1posOnChange)
        self.manhole_attribute_dlg.ui.cbP2pos.currentIndexChanged.connect(self.cbp2posOnChange)
        self.manhole_attribute_dlg.ui.cbP3pos.currentIndexChanged.connect(self.cbp3posOnChange)
        self.manhole_attribute_dlg.ui.teP1disc.textChanged.connect(self.tep1discOnChange)
        self.manhole_attribute_dlg.ui.teP2disc.textChanged.connect(self.tep2discOnChange)
        self.manhole_attribute_dlg.ui.teP3disc.textChanged.connect(self.tep3discOnChange)
        self.manhole_attribute_dlg.ui.teVx.setText("")
        self.manhole_attribute_dlg.ui.teVy.setText("")
        self.manhole_attribute_dlg.ui.btP1xy.clicked.connect(self.GetP1xy)
        self.manhole_attribute_dlg.ui.btP2xy.clicked.connect(self.GetP2xy)
        self.manhole_attribute_dlg.ui.btP3xy.clicked.connect(self.GetP3xy)
        self.manhole_attribute_dlg.ui.pushButtonOK_pin.clicked.connect(self.pin_save)

        #hydrant_attribute_dlg
        self.hydrant_attribute_dlg.ui.pushButtonOK.clicked.connect(self.hydrant_attribute_ok)
        self.hydrant_attribute_dlg.ui.pushButtonCancel.clicked.connect(self.hydrant_attribute_close)
        self.hydrant_attribute_dlg.ui.cbP1pos.currentIndexChanged.connect(self.cbp1posOnChange)
        self.hydrant_attribute_dlg.ui.cbP2pos.currentIndexChanged.connect(self.cbp2posOnChange)
        self.hydrant_attribute_dlg.ui.cbP3pos.currentIndexChanged.connect(self.cbp3posOnChange)
        self.hydrant_attribute_dlg.ui.teP1disc.textChanged.connect(self.tep1discOnChange)
        self.hydrant_attribute_dlg.ui.teP2disc.textChanged.connect(self.tep2discOnChange)
        self.hydrant_attribute_dlg.ui.teP3disc.textChanged.connect(self.tep3discOnChange)
        self.hydrant_attribute_dlg.ui.teVx.setText("")
        self.hydrant_attribute_dlg.ui.teVy.setText("")
        self.hydrant_attribute_dlg.ui.btP1xy.clicked.connect(self.GetP1xy)
        self.hydrant_attribute_dlg.ui.btP2xy.clicked.connect(self.GetP2xy)
        self.hydrant_attribute_dlg.ui.btP3xy.clicked.connect(self.GetP3xy)
        self.hydrant_attribute_dlg.ui.pushButtonOK_pin.clicked.connect(self.pin_save)
        # 選取物件
        self.edit_features_tool = IdentifyRegionTool(self.canvas)

        self.drawline = QgsMapToolEmitPoint(self.canvas)


    def unload(self):
        self.iface.removeToolBarIcon(self.action_attribute_edit)
        self.iface.removePluginMenu(u"屬性修改", self.action_attribute_edit)

        del self.toolBar

    ####################################
    #    選取物件觸發
    ####################################

    def edit_features_tool_init(self):
        self.canvas.setMapTool(self.edit_features_tool)
        self.action_attribute_edit.setChecked(True)
        QObject.connect(self.edit_features_tool, SIGNAL("featureIdentified"), self.confirm_area)

    
    def confirm_area(self, result_list):

        db_conn = self.get_db_connection()
        query_string = u'SELECT * FROM work_unit'
        query = db_conn.exec_(query_string)

        if query.isActive():
            while query.next():
                self.unitcode = query.value(0)
                print self.unitcode
        
        if not self.unitcode == u'':
            if result_list:
                self.pick_features_dlg.ui.listWidget_pick.clear()

            for result in result_list:

                gid = u' ' + unicode(result.mFeature.id())
                self.gid = gid
                #print self.gid
                if result.mLayer.name() == u'valve':
                    feature_name = u'閥'

                elif result.mLayer.name() == u'manhole':
                    feature_name = u'人手孔'
                else:
                    feature_name = u'消防栓'
                feature_name += gid
                #   清單列表(物件) --> list_item
                list_item = QListWidgetItem(feature_name)


                self.pick_features_dlg.ui.listWidget_pick.addItem(list_item)
                
                self.feature_name = feature_name
                print self.feature_name
        self.pick_features_dlg.show()    
        db_conn.close()


    def attribute_init(self):
        item_text = self.pick_features_dlg.ui.listWidget_pick.currentItem().text()

        if item_text.split(' ')[0] == u'閥':
            layer_name = 'valve'

            self.valve_attribute_init()

        
        if item_text.split(' ')[0] == u'人手孔':
            layer_name = 'manhole'

            self.manhole_attribute_init()

        if item_text.split(' ')[0] == u'消防栓':
            layer_name = 'hydrant'

            self.hydrant_attribute_init()
    

    def GetP1xy(self):
        global iButton
        iButton = 1

        self.unitcode
        if len(self.unitcode)>0:
            self.iface.mapCanvas().setMapTool(self.drawline)

            QObject.connect(self.drawline, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.confirm_geom)
        

    def GetP2xy(self):
        global iButton
        iButton = 2
        
        self.unitcode
        if len(self.unitcode)>0:
            self.iface.mapCanvas().setMapTool(self.drawline)

            QObject.connect(self.drawline, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.confirm_geom)

    def GetP3xy(self):
        global iButton
        iButton = 3

        self.unitcode
        if len(self.unitcode)>0:
            self.iface.mapCanvas().setMapTool(self.drawline)

            QObject.connect(self.drawline, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.confirm_geom)


    def confirm_geom(self, point, button):
        global iButton
        item_text = self.pick_features_dlg.ui.listWidget_pick.currentItem().text()
        
        db_conn = self.get_db_connection()
        query_string = u'SELECT * FROM work_unit'
        query = db_conn.exec_(query_string)
        if query.isActive():
            while query.next():
                self.unitcode = query.value(0)

        point_xy = str(point.x()) + u' ' + str(point.y())
        self.point_x = str(point.x())
        self.point_y = str(point.y())
        self.px = str(point.x())
        self.py = str(point.y())

        print self.point_x
        print self.point_y

        #填支點
        if item_text.split(' ')[0] == u'閥':
            xx=float(self.valve_attribute_dlg.ui.lineEdit_coord_97x.text())-point.x()
            yy=float(self.valve_attribute_dlg.ui.lineEdit_coord_97y.text())-point.y()
            equip_x=float(self.valve_attribute_dlg.ui.lineEdit_coord_97x.text())
            equip_y=float(self.valve_attribute_dlg.ui.lineEdit_coord_97y.text())
            if iButton == 1:
                self.valve_attribute_dlg.ui.teP1x.setText("%.3f" % point.x())
                self.valve_attribute_dlg.ui.teP1y.setText("%.3f" % point.y())
                self.valve_attribute_dlg.ui.teP1dis.setText("%.2f" % math.sqrt(xx*xx+yy*yy))
                txt=u"第一支點  距【%s%s】【%.2f】公尺" % (self.valve_attribute_dlg.ui.teP1disc.toPlainText(),self.valve_attribute_dlg.ui.cbP1pos.currentText(),math.sqrt(xx*xx+yy*yy))
                self.valve_attribute_dlg.ui.lbl_pin1.setText(txt)
            if iButton==2:  
                self.valve_attribute_dlg.ui.teP2x.setText("%.3f" % point.x())
                self.valve_attribute_dlg.ui.teP2y.setText("%.3f" % point.y())
                self.valve_attribute_dlg.ui.teP2dis.setText("%.2f" % math.sqrt(xx*xx+yy*yy))
                txt=u"第二支點  距【%s%s】【%.2f】公尺" % (self.valve_attribute_dlg.ui.teP2disc.toPlainText(),self.valve_attribute_dlg.ui.cbP2pos.currentText(),math.sqrt(xx*xx+yy*yy))
                self.valve_attribute_dlg.ui.lbl_pin2.setText(txt)
            if iButton==3:  
                self.valve_attribute_dlg.ui.teP3x.setText("%.3f" % point.x())
                self.valve_attribute_dlg.ui.teP3y.setText("%.3f" % point.y())
                self.valve_attribute_dlg.ui.teP3dis.setText("%.2f" % math.sqrt(xx*xx+yy*yy))
                txt=u"第三支點  距【%s%s】【%.2f】公尺" % (self.valve_attribute_dlg.ui.teP3disc.toPlainText(),self.valve_attribute_dlg.ui.cbP3pos.currentText(),math.sqrt(xx*xx+yy*yy))
                self.valve_attribute_dlg.ui.lbl_pin3.setText(txt)

        if item_text.split(' ')[0] == u'消防栓':
            xx=float(self.hydrant_attribute_dlg.ui.lineEdit_coord_97x.text())-point.x()
            yy=float(self.hydrant_attribute_dlg.ui.lineEdit_coord_97y.text())-point.y()
            equip_x=float(self.hydrant_attribute_dlg.ui.lineEdit_coord_97x.text())
            equip_y=float(self.hydrant_attribute_dlg.ui.lineEdit_coord_97y.text())
            if iButton==1:
                self.hydrant_attribute_dlg.ui.teP1x.setText("%.3f" % point.x())
                self.hydrant_attribute_dlg.ui.teP1y.setText("%.3f" % point.y())
                self.hydrant_attribute_dlg.ui.teP1dis.setText("%.2f" % math.sqrt(xx*xx+yy*yy))
                txt=u"第一支點  距【%s%s】【%.2f】公尺" % (self.hydrant_attribute_dlg.ui.teP1disc.toPlainText(),self.hydrant_attribute_dlg.ui.cbP1pos.currentText(),math.sqrt(xx*xx+yy*yy))
                self.hydrant_attribute_dlg.ui.lbl_pin1.setText(txt)
            elif iButton==2:  
                self.hydrant_attribute_dlg.ui.teP2x.setText("%.3f" % point.x())
                self.hydrant_attribute_dlg.ui.teP2y.setText("%.3f" % point.y())
                self.hydrant_attribute_dlg.ui.teP2dis.setText("%.2f" % math.sqrt(xx*xx+yy*yy))
                txt=u"第二支點  距【%s%s】【%.2f】公尺" % (self.hydrant_attribute_dlg.ui.teP2disc.toPlainText(),self.hydrant_attribute_dlg.ui.cbP2pos.currentText(),math.sqrt(xx*xx+yy*yy))
                self.hydrant_attribute_dlg.ui.lbl_pin2.setText(txt)
            elif iButton==3:  
                self.hydrant_attribute_dlg.ui.teP3x.setText("%.3f" % point.x())
                self.hydrant_attribute_dlg.ui.teP3y.setText("%.3f" % point.y())
                self.hydrant_attribute_dlg.ui.teP3dis.setText("%.2f" % math.sqrt(xx*xx+yy*yy))
                txt=u"第三支點  距【%s%s】【%.2f】公尺" % (self.hydrant_attribute_dlg.ui.teP3disc.toPlainText(),self.hydrant_attribute_dlg.ui.cbP3pos.currentText(),math.sqrt(xx*xx+yy*yy))
                self.hydrant_attribute_dlg.ui.lbl_pin3.setText(txt)
       
        if item_text.split(' ')[0] == u'人手孔':
            xx=float(self.manhole_attribute_dlg.ui.lineEdit_coord_97x.text())-point.x()
            yy=float(self.manhole_attribute_dlg.ui.lineEdit_coord_97y.text())-point.y()
            equip_x=float(self.manhole_attribute_dlg.ui.lineEdit_coord_97x.text())
            equip_y=float(self.manhole_attribute_dlg.ui.lineEdit_coord_97y.text())
            if iButton==1:
                self.manhole_attribute_dlg.ui.teP1x.setText("%.3f" % point.x())
                self.manhole_attribute_dlg.ui.teP1y.setText("%.3f" % point.y())
                self.manhole_attribute_dlg.ui.teP1dis.setText("%.2f" % math.sqrt(xx*xx+yy*yy))
                txt=u"第一支點  距【%s%s】【%.2f】公尺" % (self.manhole_attribute_dlg.ui.teP1disc.toPlainText(),self.manhole_attribute_dlg.ui.cbP1pos.currentText(),math.sqrt(xx*xx+yy*yy))
                self.manhole_attribute_dlg.ui.lbl_pin1.setText(txt)
            elif iButton==2:  
                self.manhole_attribute_dlg.ui.teP2x.setText("%.3f" % point.x())
                self.manhole_attribute_dlg.ui.teP2y.setText("%.3f" % point.y())
                self.manhole_attribute_dlg.ui.teP2dis.setText("%.2f" % math.sqrt(xx*xx+yy*yy))
                txt=u"第二支點  距【%s%s】【%.2f】公尺" % (self.manhole_attribute_dlg.ui.teP2disc.toPlainText(),self.manhole_attribute_dlg.ui.cbP2pos.currentText(),math.sqrt(xx*xx+yy*yy))
                self.manhole_attribute_dlg.ui.lbl_pin2.setText(txt)
            elif iButton==3:  
                self.manhole_attribute_dlg.ui.teP3x.setText("%.3f" % point.x())
                self.manhole_attribute_dlg.ui.teP3y.setText("%.3f" % point.y())
                self.manhole_attribute_dlg.ui.teP3dis.setText("%.2f" % math.sqrt(xx*xx+yy*yy))
                txt=u"第三支點  距【%s%s】【%.2f】公尺" % (self.manhole_attribute_dlg.ui.teP3disc.toPlainText(),self.manhole_attribute_dlg.ui.cbP3pos.currentText(),math.sqrt(xx*xx+yy*yy))
                self.manhole_attribute_dlg.ui.lbl_pin3.setText(txt)
    
        db_conn.close()
    ####################################
    #    閥類物件 - 初始化對話框
    ####################################
    def valve_attribute_init(self):
        global iButton
        
        item_text = self.pick_features_dlg.ui.listWidget_pick.currentItem().text()
        '''
        if item_text.split(' ')[0] == u'閥':
            layer_name = 'valve'

            self.hydrant_attribute_dlg.close()
            self.valve_attribute_dlg.show()
            self.manhole_attribute_dlg.close()
        '''
        self.shape_gid = int(item_text.split(' ')[1])
        self.valve_attribute_dlg.show()

        self.valve_attribute_dlg.ui.lineEdit_unific_id.setText("")

        self.valve_attribute_dlg.ui.comboBox_valve_type.clear()
        self.valve_attribute_dlg.ui.comboBox_valve_status.clear()
        self.valve_attribute_dlg.ui.comboBox_valve_sw.clear()
        self.valve_attribute_dlg.ui.comboBox_valve_mode.clear()

        # 設置下拉選單
        valve_type_list = [u'0 制水閥', u'1 制水閥(附手輪)', u'2 彈性坐封閘閥', u'3 彈性坐封閘閥(附手輪)', u'4 蝶閥(豎式)', u'5 蝶閥(橫軸式)', u'6 電動閥', 
        u'7 浮球閥', u'8 底閥', u'9 氣動閥', u'A 水力自動閥', u'B 逆止閥', u'C 排氣閥', u'D 減壓、持壓閥', u'E 洩壓閥']
        self.valve_attribute_dlg.ui.comboBox_valve_type.addItems(valve_type_list)
        valve_status_list = [u'0 正常', u'1 停用', u'2 A', u'3 M']
        self.valve_attribute_dlg.ui.comboBox_valve_status.addItems(valve_status_list)
        valve_sw_list = [u'0 順時針', u'1 逆時針']
        self.valve_attribute_dlg.ui.comboBox_valve_sw.addItems(valve_sw_list)
        valve_mode_list = [u'0 非測量', u'1 測量', u'2 合理化調整']
        self.valve_attribute_dlg.ui.comboBox_valve_mode.addItems(valve_mode_list)

        # 設置文字輸入框 文字格式
        self.valve_attribute_dlg.ui.lineEdit_valve_id.setText("")
        self.valve_attribute_dlg.ui.lineEdit_valve_id.setText("")
        self.valve_attribute_dlg.ui.lineEdit_valve_id.setDisabled(True)

        self.valve_attribute_dlg.ui.lineEdit_valve_model.clear()
        self.valve_attribute_dlg.ui.lineEdit_valve_pd.clear()
        self.valve_attribute_dlg.ui.lineEdit_bury_date.clear()
        self.valve_attribute_dlg.ui.lineEdit_bury_loc.clear()
        self.valve_attribute_dlg.ui.lineEdit_proj_name.clear()
        self.valve_attribute_dlg.ui.lineEdit_const_unit.clear()
        self.valve_attribute_dlg.ui.lineEdit_monit_name.clear()
        self.valve_attribute_dlg.ui.lineEdit_remark.clear()

        self.valve_attribute_dlg.ui.plainTextEdit_maint_date.clear()
        self.valve_attribute_dlg.ui.plainTextEdit_maint_rec.clear()
        self.valve_attribute_dlg.ui.listWidget_maint_date.clear()

        # 設置文字輸入框 數字格式
        self.valve_attribute_dlg.ui.lineEdit_angle.setText(u'000.00')
        self.valve_attribute_dlg.ui.lineEdit_valve_size.clear()
        self.valve_attribute_dlg.ui.lineEdit_valve_turn.setText(u'0')
        self.valve_attribute_dlg.ui.lineEdit_valve_time.clear()
        self.valve_attribute_dlg.ui.lineEdit_bury_depth.setText(u'0000.000')

        self.valve_attribute_dlg.ui.lineEdit_coord_97z.setText(u'0000.000')
        self.valve_attribute_dlg.ui.lineEdit_coord_67x.setText(u'000000.000')
        self.valve_attribute_dlg.ui.lineEdit_coord_67y.setText(u'0000000.000')
        self.valve_attribute_dlg.ui.lineEdit_coord_97x.setText(u'000000.000')
        self.valve_attribute_dlg.ui.lineEdit_coord_97y.setText(u'0000000.000')
        self.valve_attribute_dlg.ui.teVx.setText("")
        
        #三支距
        self.valve_attribute_dlg.ui.teP1x.setText("")
        self.valve_attribute_dlg.ui.teP1y.setText("")
        self.valve_attribute_dlg.ui.teP2x.setText("")
        self.valve_attribute_dlg.ui.teP2y.setText("")
        self.valve_attribute_dlg.ui.teP3x.setText("")
        self.valve_attribute_dlg.ui.teP3y.setText("")
        self.valve_attribute_dlg.ui.teP1disc.setText("")
        self.valve_attribute_dlg.ui.teP2disc.setText("")
        self.valve_attribute_dlg.ui.teP3disc.setText("")
        self.valve_attribute_dlg.ui.teP1dis.setText("")
        self.valve_attribute_dlg.ui.teP2dis.setText("")
        self.valve_attribute_dlg.ui.teP3dis.setText("")                   
        self.valve_attribute_dlg.ui.cbP1pos.setCurrentIndex(-1)
        self.valve_attribute_dlg.ui.cbP2pos.setCurrentIndex(-1)
        self.valve_attribute_dlg.ui.cbP3pos.setCurrentIndex(-1)
        txt=u"第一支點  距【】【】公尺" 
        self.valve_attribute_dlg.ui.lbl_pin1.setText(txt)
        txt=u"第二支點  距【】【】公尺"
        self.valve_attribute_dlg.ui.lbl_pin2.setText(txt)
        txt=u"第三支點  距【】【】公尺"
        self.valve_attribute_dlg.ui.lbl_pin3.setText(txt)


        query_string = u'SELECT * FROM valve WHERE gid={}'.format(self.shape_gid)
        
        db_conn = self.get_db_connection()
        query = db_conn.exec_(query_string)
        if query.isActive():
            while query.next():
                record = query.record()
                
                #GID
                if record.field('gid').value()!=None:
                    gid_c = unicode(record.field('gid').value())
                    self.valve_attribute_dlg.ui.tegid.setText(gid_c)

                #UID
                if (record.field('unific_id').value() !=None) and (record.field('unific_id').value() !=''):
                    print unicode(record.field('unific_id').value())
                    unific_id_c = unicode(record.field('unific_id').value())
                    self.valve_attribute_dlg.ui.lineEdit_unific_id.setText(unific_id_c)
                    self.valve_attribute_dlg.ui.teuid.setText(unific_id_c)
                    self.unific_id_c = unicode(record.field('unific_id').value())

                #self.valve_attribute_dlg.ui.btUID.setEnabled(False)            
                else:   
                    self.valve_attribute_dlg.ui.lineEdit_unific_id.setText("")     
                    #self.valve_attribute_dlg.ui.btUID.setEnabled(True)            
                #self.valve_attribute_dlg.ui.lineEdit_unific_id.setDisabled(True)


                #Angle
                if record.field('angle').value() !=None:
                    angle_c=unicode(record.field("angle").value())
                    self.valve_attribute_dlg.ui.lineEdit_angle.setText(angle_c)
                else:   
                    self.valve_attribute_dlg.ui.lineEdit_angle.setText("000.00")     


                #廠牌型號
                if record.field('valve_model').value() !=None:
                    valve_model_c=unicode(record.field("valve_model").value())
                    self.valve_attribute_dlg.ui.lineEdit_valve_model.setText(valve_model_c)
                else:   
                    self.valve_attribute_dlg.ui.lineEdit_valve_model.setText("")


                #舊編號             
                if record.field('valve_pd').value() !=None:
                    valve_pd_c=unicode(record.field("valve_pd").value())
                    self.valve_attribute_dlg.ui.lineEdit_valve_pd.setText(valve_pd_c)
                else:   
                    self.valve_attribute_dlg.ui.lineEdit_valve_pd.setText("")


                #閥類編號             
                if record.field('valve_id').value() !=None:
                    valve_id_c=unicode(record.field("valve_id").value())
                    self.valve_attribute_dlg.ui.lineEdit_valve_id.setText(valve_id_c)
                else:   
                    self.valve_attribute_dlg.ui.lineEdit_valve_id.setText("")
                    self.valve_attribute_dlg.ui.lineEdit_valve_id.setDisabled(True)


                #閥類狀態             
                if record.field('valve_status').value() !=None:
                    if record.field('valve_status')=="A":
                        self.valve_attribute_dlg.ui.comboBox_valve_type.setCurrentIndex(2)
                    elif record.field('valve_status')=="M":  
                        self.valve_attribute_dlg.ui.comboBox_valve_type.setCurrentIndex(3)
                    else:
                        self.valve_attribute_dlg.ui.comboBox_valve_status.setCurrentIndex(int(record.field("valve_status").value()))
                else:   
                    self.valve_attribute_dlg.ui.comboBox_valve_status.setCurrentIndex(0)
                #self.valve_attribute_dlg.ui.comboBox_valve_status.setCurrentIndex(-1)


                #閥類型態             
                if (record.field('valve_type').value() !=None) and (record.field('valve_type').value()!=''):
                    if record.field('valve_type')=="A":
                        self.valve_attribute_dlg.ui.comboBox_valve_type.setCurrentIndex(10)
                    elif record.field('valve_type')=="B":  
                        self.valve_attribute_dlg.ui.comboBox_valve_type.setCurrentIndex(11)
                    elif record.field('valve_type')=="C":  
                        self.valve_attribute_dlg.ui.comboBox_valve_type.setCurrentIndex(12)
                    elif record.field('valve_type')=="D":  
                        self.valve_attribute_dlg.ui.comboBox_valve_type.setCurrentIndex(13)
                    elif record.field('valve_type')=="E":  
                        self.valve_attribute_dlg.ui.comboBox_valve_type.setCurrentIndex(14)
                    else:
                        self.valve_attribute_dlg.ui.comboBox_valve_type.setCurrentIndex(int(record.field("valve_type").value()))
                else:   
                    self.valve_attribute_dlg.ui.comboBox_valve_type.setCurrentIndex(0)


                #開關轉向            
                if (record.field('valve_sw').value() !=None) and (record.field('valve_sw')!=''):
                    self.valve_attribute_dlg.ui.comboBox_valve_sw.setCurrentIndex(int(record.field("valve_sw").value()))
                else:   
                    self.valve_attribute_dlg.ui.comboBox_valve_sw.setCurrentIndex(0)


                #口徑
                #if (record.field('valve_size').value() !=None) and (record.field('valve_size')!=''):
                if record.field('valve_size').value() !=None:
                    valve_size_c=unicode(str(int(record.field("valve_size").value())))
                    self.valve_attribute_dlg.ui.lineEdit_valve_size.setText(valve_size_c)
                else:   
                    self.valve_attribute_dlg.ui.lineEdit_valve_size.setText("")     

                #轉數                 
                if record.field('valve_turn').value() !=None:
                #valve_turn_c=unicode(record.field("valve_turn"))
                    valve_turn_c=unicode(str(int(record.field("valve_turn").value())))
                    self.valve_attribute_dlg.ui.lineEdit_valve_turn.setText(valve_turn_c)
                else:
                    self.valve_attribute_dlg.ui.lineEdit_valve_turn.setText("")         

                #開關時間   
                if record.field('valve_time').value() !=None:
                    valve_time_c=unicode(record.field("valve_time").value())
                    self.valve_attribute_dlg.ui.lineEdit_valve_time.setText(valve_time_c)
                else:
                    self.valve_attribute_dlg.ui.lineEdit_valve_time.setText("")

                #埋設位置
                if record.field('bury_loc').value() !=None:
                    bury_loc_c=unicode(record.field("bury_loc").value())
                    self.valve_attribute_dlg.ui.lineEdit_bury_loc.setText(bury_loc_c)
                else:
                    self.valve_attribute_dlg.ui.lineEdit_bury_loc.setText("")

                #埋設深度
                if record.field('bury_depth').value() !=None:
                    bury_depth_c=unicode(record.field("bury_depth").value())
                    self.valve_attribute_dlg.ui.lineEdit_bury_depth.setText(bury_depth_c)
                else:
                    self.valve_attribute_dlg.ui.lineEdit_bury_depth.setText("")

                #埋設日期
                if record.field('bury_date').value() !=None:
                    bury_date_c=unicode(record.field("bury_date").value())
                    self.valve_attribute_dlg.ui.lineEdit_bury_date.setText(bury_date_c)
                else:
                    self.valve_attribute_dlg.ui.lineEdit_bury_date.setText("")

                '''
                #養護及檢查日期
                query_string = u"SELECT * FROM inspect_valve where unific_id ='"+unific_id_c+"' order by insdate DESC"
                result2 = QSqlQuery(db_twwater)
                result2 = db_twwater.exec_(query_string)
                while result2.next():
                    record = result2.record()
                    self.valve_attribute_dlg.ui.listWidget_maint_date.addItem(u"%s - %s" % (record.field('insdate').value(),record.field('status').value()))
                '''

                #監造單位
                if record.field('const_unit').value() !=None:
                    const_unit_c=unicode(record.field("const_unit").value())
                    self.valve_attribute_dlg.ui.lineEdit_const_unit.setText(const_unit_c)
                else:
                    self.valve_attribute_dlg.ui.lineEdit_const_unit.setText("")

                #工程名稱
                if record.field('proj_name').value() !=None:
                    proj_name_c=unicode(record.field("proj_name").value())
                    self.valve_attribute_dlg.ui.lineEdit_proj_name.setText(proj_name_c)
                else:
                    self.valve_attribute_dlg.ui.lineEdit_proj_name.setText("")

                #監工員
                if record.field('monit_name').value() !=None:
                    monit_name_c=unicode(record.field("monit_name").value())
                    self.valve_attribute_dlg.ui.lineEdit_monit_name.setText(monit_name_c)
                else:
                    self.valve_attribute_dlg.ui.lineEdit_monit_name.setText("")

                #註記說明
                if record.field('remark').value() !=None:
                    remark_c=unicode(record.field("remark").value())
                    self.valve_attribute_dlg.ui.lineEdit_remark.setText(remark_c)
                else:
                    self.valve_attribute_dlg.ui.lineEdit_remark.setText("")

                #測量註記
                if (record.field('valve_mode').value() !=None) and (record.field('valve_mode').value()!=''):
                    self.valve_attribute_dlg.ui.comboBox_valve_mode.setCurrentIndex(int(record.field("valve_mode").value()))
                else:
                    self.valve_attribute_dlg.ui.comboBox_valve_mode.setCurrentIndex(-1)


                if record.field('coord_97z').value() !=None:
                    coord_97z_c=unicode(record.field("coord_97z").value())
                    self.valve_attribute_dlg.ui.lineEdit_coord_97z.setText(coord_97z_c)
                else:
                    self.valve_attribute_dlg.ui.lineEdit_coord_97z.setText('0.0')

                if record.field('coord_67x').value() !=None:
                    coord_67x_c=unicode(record.field("coord_67x").value())
                    self.valve_attribute_dlg.ui.lineEdit_coord_67x.setText(coord_67x_c)
                else:
                    self.valve_attribute_dlg.ui.lineEdit_coord_67x.setText('0.0')

                if record.field('coord_67y').value() !=None:
                    coord_67y_c=unicode(record.field("coord_67y").value())
                    self.valve_attribute_dlg.ui.lineEdit_coord_67y.setText(coord_67y_c)
                else:
                    self.valve_attribute_dlg.ui.lineEdit_coord_67y.setText('0.0')

                if record.field('coord_97x').value() !=None:
                    coord_97x_c=unicode(record.field("coord_97x").value())
                    self.valve_attribute_dlg.ui.lineEdit_coord_97x.setText(coord_97x_c)
                    self.valve_attribute_dlg.ui.teVx.setText(coord_97x_c)
                    self.featX = coord_97x_c
                else:
                    self.valve_attribute_dlg.ui.lineEdit_coord_97x.setText('0.0')

                if record.field('coord_97y').value() !=None:
                    coord_97y_c=unicode(record.field("coord_97y").value())
                    self.valve_attribute_dlg.ui.lineEdit_coord_97y.setText(coord_97y_c)
                    self.valve_attribute_dlg.ui.teVy.setText(coord_97y_c)
                    self.featY = coord_97y_c
                else:
                    self.valve_attribute_dlg.ui.lineEdit_coord_97y.setText('0.0')
            
            #取出三支距屬性----------
        query_string = u" SELECT * FROM surveytie WHERE unific_id='%s'" %str(self.unific_id_c)
        print query_string
        db_conn = self.get_db_connection()
        query = db_conn.exec_(query_string)
        if query.isActive():
            while query.next():
                record = query.record()
                self.record = query.record()


                self.valve_attribute_dlg.ui.teP1x.setText(str(record.field('p1_x').value()))
                self.valve_attribute_dlg.ui.teP1y.setText(str(record.field('p1_y').value()))
                self.valve_attribute_dlg.ui.teP2x.setText(str(record.field('p2_x').value()))
                self.valve_attribute_dlg.ui.teP2y.setText(str(record.field('p2_y').value()))
                self.valve_attribute_dlg.ui.teP3x.setText(str(record.field('p3_x').value()))
                self.valve_attribute_dlg.ui.teP3y.setText(str(record.field('p3_y').value()))
                if record.field('p1_desc').value()!=NULL:
                    self.valve_attribute_dlg.ui.teP1disc.setText(record.field('p1_desc').value())
                if record.field('p2_desc').value()!=NULL:
                    self.valve_attribute_dlg.ui.teP2disc.setText(record.field('p2_desc').value())
                if record.field('p3_desc').value()!=NULL:
                    self.valve_attribute_dlg.ui.teP3disc.setText(record.field('p3_desc').value())
                
                self.valve_attribute_dlg.ui.teP1dis.setText(str(record.field('p1_dist').value()))
                self.valve_attribute_dlg.ui.teP2dis.setText(str(record.field('p2_dist').value()))
                self.valve_attribute_dlg.ui.teP3dis.setText(str(record.field('p3_dist').value()))        

                cbP1pos_index=-1
                cbP2pos_index=-1
                cbP3pos_index=-1
                if record.field('p1_type').value()!=NULL:
                	if record.field('p1_type').value()=='P1':
                	    cbP1pos_index=1
                	elif record.field('p1_type').value()=='P2':
                	    cbP1pos_index=2
                	elif record.field('p1_type').value()=='M1':
                	    cbP1pos_index=3
                	elif record.field('p1_type').value()=='M2':
                	    cbP1pos_index=4
                	elif record.field('p1_type').value()=='B1':
                	    cbP1pos_index=5
                	elif record.field('p1_type').value()=='SL':
                	    cbP1pos_index=6
                	elif record.field('p1_type').value()=='TL':
                	    cbP1pos_index=7
                	elif record.field('p1_type').value()=='D1':
                	    cbP1pos_index=8
                	elif record.field('p1_type').value()=='HC':
                	    cbP1pos_index=9
                	elif record.field('p1_type').value()=='BD':
                	    cbP1pos_index=10
                	elif record.field('p1_type').value()=='TR':
                	    cbP1pos_index=11
                	elif record.field('p1_type').value()=='BM':
                	    cbP1pos_index=12
                	elif record.field('p1_type').value()=='T1':
                	    cbP1pos_index=13
                	elif record.field('p1_type').value()=='T2':
                	    cbP1pos_index=14
                	elif record.field('p1_type').value()=='RI':
                	    cbP1pos_index=15
                	elif record.field('p1_type').value()=='WT':
                	    cbP1pos_index=16
                	elif record.field('p1_type').value()=='BW':
                	    cbP1pos_index=17
                	elif record.field('p1_type').value()=='WA':
                	    cbP1pos_index=18
                	elif record.field('p1_type').value()=='RS':
                	    cbP1pos_index=19
                	elif record.field('p1_type').value()=='WN':
                	    cbP1pos_index=20
                	elif record.field('p1_type').value()=='GP':
                	    cbP1pos_index=21
                	elif record.field('p1_type').value()=='OT':
                	    cbP1pos_index=22
                	self.valve_attribute_dlg.ui.cbP1pos.setCurrentIndex(cbP1pos_index)
                if record.field('p2_type').value()!=NULL:
                	if record.field('p2_type').value()=='P1':
                	    cbP2pos_index=1
                	elif record.field('p2_type').value()=='P2':
                	    cbP2pos_index=2
                	elif record.field('p2_type').value()=='M1':
                	    cbP2pos_index=3
                	elif record.field('p2_type').value()=='M2':
                	    cbP2pos_index=4
                	elif record.field('p2_type').value()=='B1':
                	    cbP2pos_index=5
                	elif record.field('p2_type').value()=='SL':
                	    cbP2pos_index=6
                	elif record.field('p2_type').value()=='TL':
                	    cbP2pos_index=7
                	elif record.field('p2_type').value()=='D1':
                	    cbP2pos_index=8
                	elif record.field('p2_type').value()=='HC':
                	    cbP2pos_index=9
                	elif record.field('p2_type').value()=='BD':
                	    cbP2pos_index=10
                	elif record.field('p2_type').value()=='TR':
                	    cbP2pos_index=11
                	elif record.field('p2_type').value()=='BM':
                	    cbP2pos_index=12
                	elif record.field('p2_type').value()=='T1':
                	    cbP2pos_index=13
                	elif record.field('p2_type').value()=='T2':
                	    cbP2pos_index=14
                	elif record.field('p2_type').value()=='RI':
                	    cbP2pos_index=15
                	elif record.field('p2_type').value()=='WT':
                	    cbP2pos_index=16
                	elif record.field('p2_type').value()=='BW':
                	    cbP2pos_index=17
                	elif record.field('p2_type').value()=='WA':
                	    cbP2pos_index=18
                	elif record.field('p2_type').value()=='RS':
                	    cbP2pos_index=19
                	elif record.field('p2_type').value()=='WN':
                	    cbP2pos_index=20
                	elif record.field('p2_type').value()=='GP':
                	    cbP2pos_index=21
                	elif record.field('p2_type').value()=='OT':
                	    cbP2pos_index=22
                	self.valve_attribute_dlg.ui.cbP2pos.setCurrentIndex(cbP2pos_index)
                if record.field('p3_type').value()!=NULL:
                	if record.field('p3_type').value()=='P1':
                	    cbP3pos_index=1
                	elif record.field('p3_type').value()=='P2':
                	    cbP3pos_index=2
                	elif record.field('p3_type').value()=='M1':
                	    cbP3pos_index=3
                	elif record.field('p3_type').value()=='M2':
                	    cbP3pos_index=4
                	elif record.field('p3_type').value()=='B1':
                	    cbP3pos_index=5
                	elif record.field('p3_type').value()=='SL':
                	    cbP3pos_index=6
                	elif record.field('p3_type').value()=='TL':
                	    cbP3pos_index=7
                	elif record.field('p3_type').value()=='D1':
                	    cbP3pos_index=8
                	elif record.field('p3_type').value()=='HC':
                	    cbP3pos_index=9
                	elif record.field('p3_type').value()=='BD':
                	    cbP3pos_index=10
                	elif record.field('p3_type').value()=='TR':
                	    cbP3pos_index=11
                	elif record.field('p3_type').value()=='BM':
                	    cbP3pos_index=12
                	elif record.field('p3_type').value()=='T1':
                	    cbP3pos_index=13
                	elif record.field('p3_type').value()=='T2':
                	    cbP3pos_index=14
                	elif record.field('p3_type').value()=='RI':
                	    cbP3pos_index=15
                	elif record.field('p3_type').value()=='WT':
                	    cbP3pos_index=16
                	elif record.field('p3_type').value()=='BW':
                	    cbP3pos_index=17
                	elif record.field('p3_type').value()=='WA':
                	    cbP3pos_index=18
                	elif record.field('p3_type').value()=='RS':
                	    cbP3pos_index=19
                	elif record.field('p3_type').value()=='WN':
                	    cbP3pos_index=20
                	elif record.field('p3_type').value()=='GP':
                	    cbP3pos_index=21
                	elif record.field('p3_type').value()=='OT':
                	    cbP3pos_index=22
                	self.valve_attribute_dlg.ui.cbP3pos.setCurrentIndex(cbP3pos_index)
                txt=u"第一支點  距【%s%s】【%s】公尺" % (self.valve_attribute_dlg.ui.teP1disc.toPlainText(),self.valve_attribute_dlg.ui.cbP1pos.currentText(),self.valve_attribute_dlg.ui.teP1dis.toPlainText())
                self.valve_attribute_dlg.ui.lbl_pin1.setText(txt)
                txt=u"第二支點  距【%s%s】【%s】公尺" % (self.valve_attribute_dlg.ui.teP2disc.toPlainText(),self.valve_attribute_dlg.ui.cbP2pos.currentText(),self.valve_attribute_dlg.ui.teP2dis.toPlainText())
                self.valve_attribute_dlg.ui.lbl_pin2.setText(txt)
                txt=u"第三支點  距【%s%s】【%s】公尺" % (self.valve_attribute_dlg.ui.teP3disc.toPlainText(),self.valve_attribute_dlg.ui.cbP3pos.currentText(),self.valve_attribute_dlg.ui.teP3dis.toPlainText())
                self.valve_attribute_dlg.ui.lbl_pin3.setText(txt)
        
        # 關閉資料庫連線
        db_conn.close()

    def edit_valve_ok(self):

        #   修改下拉選單 comboBox
        unific_id = u"'" + self.valve_attribute_dlg.ui.lineEdit_unific_id.text() + u"'"
        valve_type = u"'" + self.valve_attribute_dlg.ui.comboBox_valve_type.currentText().split(' ')[0] + u"'"
        valve_status = u"'" + self.valve_attribute_dlg.ui.comboBox_valve_status.currentText().split(' ')[0] + u"'"
        valve_sw = u"'" + self.valve_attribute_dlg.ui.comboBox_valve_sw.currentText().split(' ')[0] + u"'"
        valve_mode = u"'" + self.valve_attribute_dlg.ui.comboBox_valve_mode.currentText().split(' ')[0] + u"'"

        # 處理文字 lineEdit
        valve_id = u"'" + self.valve_attribute_dlg.ui.lineEdit_valve_id.text() + u"'"
        valve_model = u"'" + self.valve_attribute_dlg.ui.lineEdit_valve_model.text() + u"'"
        valve_pd = u"'" + self.valve_attribute_dlg.ui.lineEdit_valve_pd.text() + u"'"
        bury_date = u"'" + self.valve_attribute_dlg.ui.lineEdit_bury_date.text() + u"'"
        bury_loc = u"'" + self.valve_attribute_dlg.ui.lineEdit_bury_loc.text() + u"'"
        proj_name = u"'" + self.valve_attribute_dlg.ui.lineEdit_proj_name.text() + u"'"
        const_unit = u"'" + self.valve_attribute_dlg.ui.lineEdit_const_unit.text() + u"'"
        monit_name = u"'" + self.valve_attribute_dlg.ui.lineEdit_monit_name.text() + u"'"
        remark = u"'" + self.valve_attribute_dlg.ui.lineEdit_remark.text() + u"'"

        maint_date = u"'" + self.valve_attribute_dlg.ui.plainTextEdit_maint_date.toPlainText() + u"'"
        maint_rec = u"'" + self.valve_attribute_dlg.ui.plainTextEdit_maint_rec.toPlainText() + u"'"

        # 處理數字 lineEdit ，避免 數字 欄位，以空值(只有一個預設小數點)寫入 資料庫，型態不符所發生之錯誤
        if len(self.valve_attribute_dlg.ui.lineEdit_angle.text()) > 1:
            angle = float(self.valve_attribute_dlg.ui.lineEdit_angle.text())
        else:
            angle = 0.0

        if len(self.valve_attribute_dlg.ui.lineEdit_valve_size.text()) > 1:
            valve_size = int(self.valve_attribute_dlg.ui.lineEdit_valve_size.text())
        else:
            valve_size = 0

        #if len(self.valve_attribute_dlg.ui.lineEdit_valve_turn.text()) > 1:
        if int(self.valve_attribute_dlg.ui.lineEdit_valve_turn.text()) > 0:
            valve_turn = int(self.valve_attribute_dlg.ui.lineEdit_valve_turn.text())
        else:
            valve_turn = 0

        if len(self.valve_attribute_dlg.ui.lineEdit_valve_time.text()) > 1:
            valve_time = int(self.valve_attribute_dlg.ui.lineEdit_valve_time.text())
        else:
            valve_time = 0
        
        if len(self.valve_attribute_dlg.ui.lineEdit_bury_depth.text()) > 1:
            bury_depth = float(self.valve_attribute_dlg.ui.lineEdit_bury_depth.text())
        else:
            bury_depth = 0.0

        if len(self.valve_attribute_dlg.ui.lineEdit_coord_97z.text()) > 1:
            coord_97z = float(self.valve_attribute_dlg.ui.lineEdit_coord_97z.text())
        else:
            coord_97z = 0.0

        if len(self.valve_attribute_dlg.ui.lineEdit_coord_67x.text()) > 1:
            coord_67x = float(self.valve_attribute_dlg.ui.lineEdit_coord_67x.text())
        else:
            coord_67x = 0.0

        if len(self.valve_attribute_dlg.ui.lineEdit_coord_67y.text()) > 1:
            coord_67y = float(self.valve_attribute_dlg.ui.lineEdit_coord_67y.text())
        else:
            coord_67y = 0.0

        if len(self.valve_attribute_dlg.ui.lineEdit_coord_97x.text()) > 1:
            coord_97x = float(self.valve_attribute_dlg.ui.lineEdit_coord_97x.text())
        else:
            coord_97x = 0.0

        if len(self.valve_attribute_dlg.ui.lineEdit_coord_97y.text()) > 1:
            coord_97y = float(self.valve_attribute_dlg.ui.lineEdit_coord_97y.text())
        else:
            coord_97y = 0.0

        #   SQL 指令修改表格資料
        db_conn = self.get_db_connection()

        query_string = u"UPDATE valve set unific_id={}, valve_type={}, valve_status={}, valve_sw={}, valve_mode={}, valve_model={}, valve_pd={}, bury_date={}, bury_loc={}, proj_name={}, " \
        "const_unit={}, monit_name={}, remark={}, maint_date={}, maint_rec={}, angle={}, valve_size={}, valve_turn={}, valve_time={}, bury_depth={}, coord_97z={}, coord_67x={}, " \
        "coord_67y={}, coord_97x={}, coord_97y={} where gid={}" \
        ''.format(unific_id, valve_type, valve_status, valve_sw, valve_mode, valve_model, valve_pd, bury_date, bury_loc, proj_name, \
        const_unit, monit_name, remark, maint_date, maint_rec, angle, valve_size, valve_turn, valve_time, bury_depth, coord_97z, coord_67x, coord_67y, coord_97x, coord_97y, self.shape_gid)
        
        db_conn = self.get_db_connection()
        query = db_conn.exec_(query_string)
        # 檢查執行的 query 是否為有效!
        if query.isActive():
            query.clear()
            self.valve_attribute_dlg.close()
            self.iface.mapCanvas().refresh()
            QMessageBox.information(self.iface.mainWindow(), u'修改閥類', u'資料修改完成!')
        else:
            QMessageBox.warning(self.iface.mainWindow(), u'修改閥類', u'資料庫寫入失敗!')
            
        # 關閉資料庫連線
        db_conn.close()
        


    def manhole_attribute_init(self):
        
        item_text = self.pick_features_dlg.ui.listWidget_pick.currentItem().text()
        '''
        if item_text.split(' ')[0] == u'人手孔':
            layer_name = 'manhole'
            self.manhole_attribute_dlg.show()
        '''
        self.shape_gid = int(item_text.split(' ')[1])
        self.manhole_attribute_dlg.show()
        

        # 呼叫取得序號方法
        self.manhole_attribute_dlg.ui.lineEdit_unific_id.setText("")
        self.manhole_attribute_dlg.ui.comboBox_mhole_type.clear()
        self.manhole_attribute_dlg.ui.comboBox_mhole_status.clear()
        self.manhole_attribute_dlg.ui.comboBox_mhole_mode.clear()
        self.manhole_attribute_dlg.ui.comboBox_cover_type.clear()
        self.manhole_attribute_dlg.ui.comboBox_oper_phase.clear()

        # 設置下拉選單
        mhole_type_list = [u'M1', u'M2', u'M3']
        self.manhole_attribute_dlg.ui.comboBox_mhole_type.addItems(mhole_type_list)
        mhole_status_list = [u'0 正常', u'1 停用']
        self.manhole_attribute_dlg.ui.comboBox_mhole_status.addItems(mhole_status_list)
        mhole_mode_list = [u'0 非測量點', u'1 測量點', u'2 合理化調整']
        self.manhole_attribute_dlg.ui.comboBox_mhole_mode.addItems(mhole_mode_list)
        cover_type_list = [u'0 圓孔', u'1 方孔',u'2 圓孔']
        self.manhole_attribute_dlg.ui.comboBox_cover_type.addItems(cover_type_list)
        oper_phase_list = [u'0 廢棄管', u'1 新建使用中', u'2 更動使用中']
        self.manhole_attribute_dlg.ui.comboBox_oper_phase.addItems(oper_phase_list)

        # 設置文字輸入框 文字格式
        self.manhole_attribute_dlg.ui.lineEdit_mhole_id.setText("")
        self.manhole_attribute_dlg.ui.lineEdit_mhole_id.setDisabled(True)
        self.manhole_attribute_dlg.ui.lineEdit_admin_unit.clear()
        self.manhole_attribute_dlg.ui.lineEdit_bury_date.clear()
        self.manhole_attribute_dlg.ui.lineEdit_assets_code.clear()
        self.manhole_attribute_dlg.ui.lineEdit_const_unit.clear()
        self.manhole_attribute_dlg.ui.lineEdit_bury_loc.clear()
        self.manhole_attribute_dlg.ui.lineEdit_proj_name.clear()
        self.manhole_attribute_dlg.ui.lineEdit_maint_rec.clear()
        self.manhole_attribute_dlg.ui.lineEdit_remark.clear()

        self.manhole_attribute_dlg.ui.plainTextEdit_maint_date.clear()
        self.manhole_attribute_dlg.ui.listWidget_maint_date.clear()

        # 設置文字輸入框 數字格式

        self.manhole_attribute_dlg.ui.lineEdit_angle.setText(u'000.00')
        self.manhole_attribute_dlg.ui.lineEdit_cover_width.setText(u'0000.000')
        self.manhole_attribute_dlg.ui.lineEdit_cover_length.setText(u'0000.000')
        self.manhole_attribute_dlg.ui.lineEdit_offset_dist.setText(u'0000.000')
        self.manhole_attribute_dlg.ui.lineEdit_base_elev.setText(u'0000.000')
        self.manhole_attribute_dlg.ui.lineEdit_botm_elev.setText(u'0000.000')
        self.manhole_attribute_dlg.ui.lineEdit_mhole_depth.setText(u'0000.000')

        self.manhole_attribute_dlg.ui.lineEdit_coord_67x.setText(u'00000000.000')
        self.manhole_attribute_dlg.ui.lineEdit_coord_67y.setText(u'00000000.000')
        self.manhole_attribute_dlg.ui.lineEdit_coord_97x.setText(u'00000000.000')
        self.manhole_attribute_dlg.ui.lineEdit_coord_97y.setText(u'00000000.000')

        #三支距
        self.manhole_attribute_dlg.ui.teP1x.setText("")
        self.manhole_attribute_dlg.ui.teP1y.setText("")
        self.manhole_attribute_dlg.ui.teP2x.setText("")
        self.manhole_attribute_dlg.ui.teP2y.setText("")
        self.manhole_attribute_dlg.ui.teP3x.setText("")
        self.manhole_attribute_dlg.ui.teP3y.setText("")
        self.manhole_attribute_dlg.ui.teP1disc.setText("")
        self.manhole_attribute_dlg.ui.teP2disc.setText("")
        self.manhole_attribute_dlg.ui.teP3disc.setText("")
        self.manhole_attribute_dlg.ui.teP1dis.setText("")
        self.manhole_attribute_dlg.ui.teP2dis.setText("")
        self.manhole_attribute_dlg.ui.teP3dis.setText("")                   
        self.manhole_attribute_dlg.ui.cbP1pos.setCurrentIndex(-1)
        self.manhole_attribute_dlg.ui.cbP2pos.setCurrentIndex(-1)
        self.manhole_attribute_dlg.ui.cbP3pos.setCurrentIndex(-1)
        txt=u"第一支點  距【】【】公尺" 
        self.manhole_attribute_dlg.ui.lbl_pin1.setText(txt)
        txt=u"第二支點  距【】【】公尺"
        self.manhole_attribute_dlg.ui.lbl_pin2.setText(txt)
        txt=u"第三支點  距【】【】公尺"
        self.manhole_attribute_dlg.ui.lbl_pin3.setText(txt)

        
        
        db_conn = self.get_db_connection()
        query_string = u'SELECT * FROM manhole WHERE gid={}'.format(self.shape_gid)
        query = db_conn.exec_(query_string)
        if query.isActive():
            while query.next():
                record = query.record()
                
                
                #GID
                if record.field('gid').value()!=None:
                    gid_c = unicode(record.field('gid').value())
                    self.manhole_attribute_dlg.ui.tegid.setText(gid_c)

                
                #UID
                if (record.field('unific_id').value() !=None) and (record.field('unific_id').value() !=''):
                    unific_id_c = unicode(record.field('unific_id').value())
                    self.manhole_attribute_dlg.ui.lineEdit_unific_id.setText(unific_id_c)
                    self.manhole_attribute_dlg.ui.teuid.setText(unific_id_c)
                    self.unific_id_c = unicode(record.field('unific_id').value())
                    #self.manhole_attribute_dlg.ui.btUID.setEnabled(False)            
                else:   
                    self.manhole_attribute_dlg.ui.lineEdit_unific_id.setText("")     
                    #self.manhole_attribute_dlg.ui.btUID.setEnabled(True)            
                    #self.manhole_attribute_dlg.ui.lineEdit_unific_id.setDisabled(True)

                

                #管理單位             
                if record.field('admin_unit').value() !=None:
                    admin_unit_c=unicode(record.field("admin_unit").value())
                    self.manhole_attribute_dlg.ui.lineEdit_admin_unit.setText(admin_unit_c)
                else:   
                    self.manhole_attribute_dlg.ui.lineEdit_admin_unit.setText("")


                #人孔編號             
                if record.field('mhole_id').value() !=None:
                    mhole_id_c=unicode(record.field("mhole_id").value())
                    self.manhole_attribute_dlg.ui.lineEdit_mhole_id.setText(mhole_id_c)
                else:   
                    self.manhole_attribute_dlg.ui.lineEdit_mhole_id.setText("")
                    self.manhole_attribute_dlg.ui.lineEdit_mhole_id.setDisabled(True)


                #作業區分             
                if (record.field('oper_phase').value() !=None) and (record.field('oper_phase').value() !=''):
                    self.manhole_attribute_dlg.ui.comboBox_oper_phase.setCurrentIndex(int(record.field("oper_phase").value()))
                else:   
                    self.manhole_attribute_dlg.ui.comboBox_oper_phase.setCurrentIndex(-1)
                

                #人孔狀態             
                if (record.field('mhole_status').value() !=None) and (record.field('mhole_status').value() !=''):
                    self.manhole_attribute_dlg.ui.comboBox_mhole_status.setCurrentIndex(int(record.field("mhole_status").value()))
                else:   
                    self.manhole_attribute_dlg.ui.comboBox_mhole_status.setCurrentIndex(-1)
                    

                #測量註記
                if (record.field('mhole_mode').value() !=None) and (record.field('mhole_mode').value() !=''):
                    self.manhole_attribute_dlg.ui.comboBox_mhole_mode.setCurrentIndex(int(record.field("mhole_mode").value()))
                else:
                    self.manhole_attribute_dlg.ui.comboBox_mhole_mode.setCurrentIndex(-1)


                '''
                #人孔種類             
                if (record.field('mhole_type').value() !=None):
                    self.manhole_attribute_dlg.ui.comboBox_mhole_type.setCurrentIndex(int(record.field("mhole_mode").value()))
                else:   
                    self.manhole_attribute_dlg.ui.comboBox_mhole_type.setCurrentIndex(-1)
                '''

                #孔蓋種類             
                if (record.field('cover_type').value() !=None) and (record.field('cover_type').value() !=''):
                    self.manhole_attribute_dlg.ui.comboBox_cover_type.setCurrentIndex(int(record.field("cover_type").value()))
                else:   
                    self.manhole_attribute_dlg.ui.comboBox_cover_type.setCurrentIndex(-1)


                #蓋部寬度
                if record.field('cover_width').value() !=None:
                    cover_width_c=unicode(record.field("cover_width").value())
                    self.manhole_attribute_dlg.ui.lineEdit_cover_width.setText(cover_width_c)
                else:   
                    self.manhole_attribute_dlg.ui.lineEdit_cover_width.setText('0.0')     


                #蓋部長度
                if record.field('cover_length').value() !=None:
                    cover_length_c=unicode(record.field("cover_length").value())
                    self.manhole_attribute_dlg.ui.lineEdit_cover_length.setText(cover_length_c)
                else:   
                    self.manhole_attribute_dlg.ui.lineEdit_cover_length.setText('0.0')     


                #偏心距
                if record.field('offset_dist').value() !=None:
                    offset_dist_c=unicode(record.field("offset_dist").value())
                    self.manhole_attribute_dlg.ui.lineEdit_offset_dist.setText(offset_dist_c)
                else:   
                    self.manhole_attribute_dlg.ui.lineEdit_offset_dist.setText('0.0')     


                #地盤高
                if record.field('base_elev').value() !=None:
                    base_elev_c=unicode(record.field("base_elev").value())
                    self.manhole_attribute_dlg.ui.lineEdit_base_elev.setText(base_elev_c)
                else:   
                    self.manhole_attribute_dlg.ui.lineEdit_base_elev.setText('0.0')  


                #孔底高
                if record.field('botm_elev').value() !=None:
                    botm_elev_c=unicode(record.field("botm_elev").value())
                    self.manhole_attribute_dlg.ui.lineEdit_botm_elev.setText(botm_elev_c)
                else:   
                    self.manhole_attribute_dlg.ui.lineEdit_botm_elev.setText('0.0')  


                #孔深
                if record.field('mhole_depth').value() !=None:
                    mhole_depth_c=unicode(record.field("mhole_depth").value())
                    self.manhole_attribute_dlg.ui.lineEdit_mhole_depth.setText(mhole_depth_c)
                else:
                    self.manhole_attribute_dlg.ui.lineEdit_mhole_depth.setText("0.0")
                

                #埋設日期
                if record.field('bury_date').value() !=None:
                    bury_date_c=unicode(record.field("bury_date").value())
                    self.manhole_attribute_dlg.ui.lineEdit_bury_date.setText(bury_date_c)
                else:
                    self.manhole_attribute_dlg.ui.lineEdit_bury_date.setText("")


                #埋設位置
                if record.field('bury_loc').value() !=None:
                    bury_loc_c=unicode(record.field("bury_loc").value())
                    self.manhole_attribute_dlg.ui.lineEdit_bury_loc.setText(bury_loc_c)
                else:
                    self.manhole_attribute_dlg.ui.lineEdit_bury_loc.setText("")
                
                '''
                #養護及檢查日期
                query_string = u"SELECT * FROM inspect_manhole where unific_id ='"+unific_id_c+"' order by insdate DESC"
                result2 = QSqlQuery(db_twwater)
                result2 = db_twwater.exec_(query_string)
                while result2.next():
                record = result2.record()
                self.manhole_attribute_dlg.ui.listWidget_maint_date.addItem(u"%s - %s" % (record.field('insdate').value(),record.field('status').value()))
                '''


                #監造單位
                if record.field('const_unit').value() !=None:
                    const_unit_c=unicode(record.field("const_unit").value())
                    self.manhole_attribute_dlg.ui.lineEdit_const_unit.setText(const_unit_c)
                else:
                    self.manhole_attribute_dlg.ui.lineEdit_const_unit.setText("")


                #工程名稱
                if record.field('proj_name').value() !=None:
                    proj_name_c=unicode(record.field("proj_name").value())
                    self.manhole_attribute_dlg.ui.lineEdit_proj_name.setText(proj_name_c)
                else:
                    self.manhole_attribute_dlg.ui.lineEdit_proj_name.setText("")


                #財產編號
                if record.field('assets_code').value() !=None:
                    assets_code_c=unicode(record.field("assets_code").value())
                    self.manhole_attribute_dlg.ui.lineEdit_assets_code.setText(assets_code_c)
                else:
                    self.manhole_attribute_dlg.ui.lineEdit_assets_code.setText("")


                #註記說明
                if record.field('remark').value() !=None:
                    remark_c=unicode(record.field("remark").value())
                    self.manhole_attribute_dlg.ui.lineEdit_remark.setText(remark_c)
                else:
                    self.manhole_attribute_dlg.ui.lineEdit_remark.setText("")
                

                if record.field('coord_67x').value() !=None:
                    coord_67x_c=unicode(record.field("coord_67x").value())
                    self.manhole_attribute_dlg.ui.lineEdit_coord_67x.setText(coord_67x_c)
                else:
                    self.manhole_attribute_dlg.ui.lineEdit_coord_67x.setText('0.0')
                

                if record.field('coord_67y').value() !=None:
                    coord_67y_c=unicode(record.field("coord_67y").value())
                    self.manhole_attribute_dlg.ui.lineEdit_coord_67y.setText(coord_67y_c)
                else:
                    self.manhole_attribute_dlg.ui.lineEdit_coord_67y.setText('0.0')
                

                if record.field('coord_97x').value() !=None:
                    coord_97x_c=unicode(record.field("coord_97x").value())
                    self.manhole_attribute_dlg.ui.lineEdit_coord_97x.setText(coord_97x_c)
                    self.manhole_attribute_dlg.ui.teVx.setText(coord_97x_c)
                    self.featX = coord_97x_c
                else:
                    self.manhole_attribute_dlg.ui.lineEdit_coord_97x.setText('0.0')


                if record.field('coord_97y').value() !=None:
                    coord_97y_c=unicode(record.field("coord_97y").value())
                    self.manhole_attribute_dlg.ui.lineEdit_coord_97y.setText(coord_97y_c)
                    self.manhole_attribute_dlg.ui.teVy.setText(coord_97y_c)
                    self.featY = coord_97y_c
                else:
                    self.manhole_attribute_dlg.ui.lineEdit_coord_97y.setText('0.0')


                #旋轉角度
                if record.field('angle').value() !=None:
                    angle_c=unicode(record.field("angle").value())
                    self.manhole_attribute_dlg.ui.lineEdit_angle.setText(angle_c)
                else:
                    self.manhole_attribute_dlg.ui.lineEdit_angle.setText('0.0')
        
            #取出三支距屬性----------
        query_string = u"SELECT * FROM surveytie WHERE unific_id='%s'" %str(self.unific_id_c)
        db_conn = self.get_db_connection()
        query = db_conn.exec_(query_string)
        if query.isActive():
            while query.next():
                record = query.record()


                self.manhole_attribute_dlg.ui.teP1x.setText(str(record.field('p1_x').value()))
                self.manhole_attribute_dlg.ui.teP1y.setText(str(record.field('p1_y').value()))
                self.manhole_attribute_dlg.ui.teP2x.setText(str(record.field('p2_x').value()))
                self.manhole_attribute_dlg.ui.teP2y.setText(str(record.field('p2_y').value()))
                self.manhole_attribute_dlg.ui.teP3x.setText(str(record.field('p3_x').value()))
                self.manhole_attribute_dlg.ui.teP3y.setText(str(record.field('p3_y').value()))
                if record.field('p1_desc').value()!=NULL:
                    self.manhole_attribute_dlg.ui.teP1disc.setText(record.field('p1_desc').value())
                if record.field('p2_desc').value()!=NULL:
                    self.manhole_attribute_dlg.ui.teP2disc.setText(record.field('p2_desc').value())
                if record.field('p3_desc').value()!=NULL:
                    self.manhole_attribute_dlg.ui.teP3disc.setText(record.field('p3_desc').value())
                
                self.manhole_attribute_dlg.ui.teP1dis.setText(str(record.field('p1_dist').value()))
                self.manhole_attribute_dlg.ui.teP2dis.setText(str(record.field('p2_dist').value()))
                self.manhole_attribute_dlg.ui.teP3dis.setText(str(record.field('p3_dist').value()))        

                cbP1pos_index=-1
                cbP2pos_index=-1
                cbP3pos_index=-1
                if record.field('p1_type').value()!=NULL:
                    if record.field('p1_type').value()=='P1':
                        cbP1pos_index=1
                    elif record.field('p1_type').value()=='P2':
                        cbP1pos_index=2
                    elif record.field('p1_type').value()=='M1':
                        cbP1pos_index=3
                    elif record.field('p1_type').value()=='M2':
                        cbP1pos_index=4
                    elif record.field('p1_type').value()=='B1':
                        cbP1pos_index=5
                    elif record.field('p1_type').value()=='SL':
                        cbP1pos_index=6
                    elif record.field('p1_type').value()=='TL':
                        cbP1pos_index=7
                    elif record.field('p1_type').value()=='D1':
                        cbP1pos_index=8
                    elif record.field('p1_type').value()=='HC':
                        cbP1pos_index=9
                    elif record.field('p1_type').value()=='BD':
                        cbP1pos_index=10
                    elif record.field('p1_type').value()=='TR':
                        cbP1pos_index=11
                    elif record.field('p1_type').value()=='BM':
                        cbP1pos_index=12
                    elif record.field('p1_type').value()=='T1':
                        cbP1pos_index=13
                    elif record.field('p1_type').value()=='T2':
                        cbP1pos_index=14
                    elif record.field('p1_type').value()=='RI':
                        cbP1pos_index=15
                    elif record.field('p1_type').value()=='WT':
                        cbP1pos_index=16
                    elif record.field('p1_type').value()=='BW':
                        cbP1pos_index=17
                    elif record.field('p1_type').value()=='WA':
                        cbP1pos_index=18
                    elif record.field('p1_type').value()=='RS':
                        cbP1pos_index=19
                    elif record.field('p1_type').value()=='WN':
                        cbP1pos_index=20
                    elif record.field('p1_type').value()=='GP':
                        cbP1pos_index=21
                    elif record.field('p1_type').value()=='OT':
                        cbP1pos_index=22
                    self.manhole_attribute_dlg.ui.cbP1pos.setCurrentIndex(cbP1pos_index)
                if record.field('p2_type').value()!=NULL:
                    if record.field('p2_type').value()=='P1':
                        cbP2pos_index=1
                    elif record.field('p2_type').value()=='P2':
                        cbP2pos_index=2
                    elif record.field('p2_type').value()=='M1':
                        cbP2pos_index=3
                    elif record.field('p2_type').value()=='M2':
                        cbP2pos_index=4
                    elif record.field('p2_type').value()=='B1':
                        cbP2pos_index=5
                    elif record.field('p2_type').value()=='SL':
                        cbP2pos_index=6
                    elif record.field('p2_type').value()=='TL':
                        cbP2pos_index=7
                    elif record.field('p2_type').value()=='D1':
                        cbP2pos_index=8
                    elif record.field('p2_type').value()=='HC':
                        cbP2pos_index=9
                    elif record.field('p2_type').value()=='BD':
                        cbP2pos_index=10
                    elif record.field('p2_type').value()=='TR':
                        cbP2pos_index=11
                    elif record.field('p2_type').value()=='BM':
                        cbP2pos_index=12
                    elif record.field('p2_type').value()=='T1':
                        cbP2pos_index=13
                    elif record.field('p2_type').value()=='T2':
                        cbP2pos_index=14
                    elif record.field('p2_type').value()=='RI':
                        cbP2pos_index=15
                    elif record.field('p2_type').value()=='WT':
                        cbP2pos_index=16
                    elif record.field('p2_type').value()=='BW':
                        cbP2pos_index=17
                    elif record.field('p2_type').value()=='WA':
                        cbP2pos_index=18
                    elif record.field('p2_type').value()=='RS':
                        cbP2pos_index=19
                    elif record.field('p2_type').value()=='WN':
                        cbP2pos_index=20
                    elif record.field('p2_type').value()=='GP':
                        cbP2pos_index=21
                    elif record.field('p2_type').value()=='OT':
                        cbP2pos_index=22
                    self.manhole_attribute_dlg.ui.cbP2pos.setCurrentIndex(cbP2pos_index)
                if record.field('p3_type').value()!=NULL:
                    if record.field('p3_type').value()=='P1':
                        cbP3pos_index=1
                    elif record.field('p3_type').value()=='P2':
                        cbP3pos_index=2
                    elif record.field('p3_type').value()=='M1':
                        cbP3pos_index=3
                    elif record.field('p3_type').value()=='M2':
                        cbP3pos_index=4
                    elif record.field('p3_type').value()=='B1':
                        cbP3pos_index=5
                    elif record.field('p3_type').value()=='SL':
                        cbP3pos_index=6
                    elif record.field('p3_type').value()=='TL':
                        cbP3pos_index=7
                    elif record.field('p3_type').value()=='D1':
                        cbP3pos_index=8
                    elif record.field('p3_type').value()=='HC':
                        cbP3pos_index=9
                    elif record.field('p3_type').value()=='BD':
                        cbP3pos_index=10
                    elif record.field('p3_type').value()=='TR':
                        cbP3pos_index=11
                    elif record.field('p3_type').value()=='BM':
                        cbP3pos_index=12
                    elif record.field('p3_type').value()=='T1':
                        cbP3pos_index=13
                    elif record.field('p3_type').value()=='T2':
                        cbP3pos_index=14
                    elif record.field('p3_type').value()=='RI':
                        cbP3pos_index=15
                    elif record.field('p3_type').value()=='WT':
                        cbP3pos_index=16
                    elif record.field('p3_type').value()=='BW':
                        cbP3pos_index=17
                    elif record.field('p3_type').value()=='WA':
                        cbP3pos_index=18
                    elif record.field('p3_type').value()=='RS':
                        cbP3pos_index=19
                    elif record.field('p3_type').value()=='WN':
                        cbP3pos_index=20
                    elif record.field('p3_type').value()=='GP':
                        cbP3pos_index=21
                    elif record.field('p3_type').value()=='OT':
                        cbP3pos_index=22
                    self.manhole_attribute_dlg.ui.cbP3pos.setCurrentIndex(cbP3pos_index)
                txt=u"第一支點  距【%s%s】【%s】公尺" % (self.manhole_attribute_dlg.ui.teP1disc.toPlainText(),self.manhole_attribute_dlg.ui.cbP1pos.currentText(),self.manhole_attribute_dlg.ui.teP1dis.toPlainText())
                self.manhole_attribute_dlg.ui.lbl_pin1.setText(txt)
                txt=u"第二支點  距【%s%s】【%s】公尺" % (self.manhole_attribute_dlg.ui.teP2disc.toPlainText(),self.manhole_attribute_dlg.ui.cbP2pos.currentText(),self.manhole_attribute_dlg.ui.teP2dis.toPlainText())
                self.manhole_attribute_dlg.ui.lbl_pin2.setText(txt)
                txt=u"第三支點  距【%s%s】【%s】公尺" % (self.manhole_attribute_dlg.ui.teP3disc.toPlainText(),self.manhole_attribute_dlg.ui.cbP3pos.currentText(),self.manhole_attribute_dlg.ui.teP3dis.toPlainText())
                self.manhole_attribute_dlg.ui.lbl_pin3.setText(txt)
        
                # 關閉資料庫連線
                db_conn.close()

        
    def edit_manhole_ok(self):

        unific_id = u"'" + self.manhole_attribute_dlg.ui.lineEdit_unific_id.text() + u"'"
        mhole_type = u"'" + self.manhole_attribute_dlg.ui.comboBox_mhole_type.currentText() + u"'"
        mhole_status = u"'" + self.manhole_attribute_dlg.ui.comboBox_mhole_status.currentText().split(' ')[0] + u"'"
        mhole_mode = u"'" + self.manhole_attribute_dlg.ui.comboBox_mhole_mode.currentText().split(' ')[0] + u"'"
        cover_type = u"'" + self.manhole_attribute_dlg.ui.comboBox_cover_type.currentText().split(' ')[0] + u"'"
        oper_phase = u"'" + self.manhole_attribute_dlg.ui.comboBox_oper_phase.currentText().split(' ')[0] + u"'"

        # 處理文字 lineEdit
        mhole_id = u"'" + self.manhole_attribute_dlg.ui.lineEdit_mhole_id.text() + u"'"
        admin_unit = u"'" + self.manhole_attribute_dlg.ui.lineEdit_admin_unit.text() + u"'"
        bury_date = u"'" + self.manhole_attribute_dlg.ui.lineEdit_bury_date.text() + u"'"
        assets_code = u"'" + self.manhole_attribute_dlg.ui.lineEdit_assets_code.text() + u"'"
        const_unit = u"'" + self.manhole_attribute_dlg.ui.lineEdit_const_unit.text() + u"'"
        bury_loc = u"'" + self.manhole_attribute_dlg.ui.lineEdit_bury_loc.text() + u"'"
        proj_name = u"'" + self.manhole_attribute_dlg.ui.lineEdit_proj_name.text() + u"'"
        maint_rec = u"'" + self.manhole_attribute_dlg.ui.lineEdit_maint_rec.text() + u"'"
        remark = u"'" + self.manhole_attribute_dlg.ui.lineEdit_remark.text() + u"'"

        maint_date = u"'" + self.manhole_attribute_dlg.ui.plainTextEdit_maint_date.toPlainText() + u"'"

        # 處理數字 lineEdit ，避免 數字 欄位，以空值(只有一個預設小數點)寫入 資料庫，型態不符所發生之錯誤
        if len(self.manhole_attribute_dlg.ui.lineEdit_cover_width.text()) > 1:
            cover_width = float(self.manhole_attribute_dlg.ui.lineEdit_cover_width.text())
        else:
            cover_width = 0.0

        if len(self.manhole_attribute_dlg.ui.lineEdit_cover_length.text()) > 1:
            cover_length = float(self.manhole_attribute_dlg.ui.lineEdit_cover_length.text())
        else:
            cover_length = 0.0

        if len(self.manhole_attribute_dlg.ui.lineEdit_offset_dist.text()) > 1:
            offset_dist = float(self.manhole_attribute_dlg.ui.lineEdit_offset_dist.text())
        else:
            offset_dist = 0.0

        if len(self.manhole_attribute_dlg.ui.lineEdit_base_elev.text()) > 1:
            base_elev = float(self.manhole_attribute_dlg.ui.lineEdit_base_elev.text())
        else:
            base_elev = 0.0
        
        if len(self.manhole_attribute_dlg.ui.lineEdit_botm_elev.text()) > 1:
            botm_elev = float(self.manhole_attribute_dlg.ui.lineEdit_botm_elev.text())
        else:
            botm_elev = 0.0

        if len(self.manhole_attribute_dlg.ui.lineEdit_mhole_depth.text()) > 1:
            mhole_depth = float(self.manhole_attribute_dlg.ui.lineEdit_mhole_depth.text())
        else:
            mhole_depth = 0.0

        if len(self.manhole_attribute_dlg.ui.lineEdit_coord_67x.text()) > 1:
            coord_67x = float(self.manhole_attribute_dlg.ui.lineEdit_coord_67x.text())
        else:
            coord_67x = 0.0

        if len(self.manhole_attribute_dlg.ui.lineEdit_coord_67y.text()) > 1:
            coord_67y = float(self.manhole_attribute_dlg.ui.lineEdit_coord_67y.text())
        else:
            coord_67y = 0.0

        if len(self.manhole_attribute_dlg.ui.lineEdit_coord_97x.text()) > 1:
            coord_97x = float(self.manhole_attribute_dlg.ui.lineEdit_coord_97x.text())
        else:
            coord_97x = 0.0

        if len(self.manhole_attribute_dlg.ui.lineEdit_coord_97y.text()) > 1:
            coord_97y = float(self.manhole_attribute_dlg.ui.lineEdit_coord_97y.text())
        else:
            coord_97y = 0.0

        if len(self.manhole_attribute_dlg.ui.lineEdit_angle.text()) > 1:
            angle = float(self.manhole_attribute_dlg.ui.lineEdit_angle.text())
        else:
            angle = 0.0


        #   SQL 指令修改表格資料
        db_conn = self.get_db_connection()

        query_string = u"UPDATE manhole set unific_id={}, mhole_type={}, mhole_status={}, mhole_mode={}, cover_type={}, oper_phase={}, mhole_id={}, admin_unit={}, bury_date={}, " \
        "assets_code={}, const_unit={}, bury_loc={}, proj_name={}, maint_rec={}, remark={}, maint_date={}, cover_width={}, cover_length={}, offset_dist={}, " \
        "base_elev={}, botm_elev={}, mhole_depth={}, coord_67x={}, coord_67y={}, coord_97x={}, coord_97y={}, angle={} where gid={}" \
        ''.format(unific_id, mhole_type, mhole_status, mhole_mode, cover_type, oper_phase, mhole_id, admin_unit, bury_date, assets_code, const_unit, \
        bury_loc, proj_name, maint_rec, remark, maint_date, cover_width, cover_length, offset_dist, base_elev, botm_elev, mhole_depth, coord_67x, coord_67y, coord_97x, coord_97y, angle, self.shape_gid)
        print query_string
        db_conn = self.get_db_connection()
        query = db_conn.exec_(query_string)
        # 檢查執行的 query 是否為有效!
        if query.isActive():
            query.clear()
            self.manhole_attribute_dlg.close()
            self.iface.mapCanvas().refresh()
            QMessageBox.information(self.iface.mainWindow(), u'修改人手孔', u'資料修改完成!')
        else:
            QMessageBox.warning(self.iface.mainWindow(), u'修改人手孔', u'資料庫修改失敗!')
        # 關閉資料庫連線
        db_conn.close()
        
    
    def hydrant_attribute_init(self):

        item_text = self.pick_features_dlg.ui.listWidget_pick.currentItem().text()
        '''
        if item_text.split(' ')[0] == u'消防栓':
            layer_name = 'hydrant'
            self.hydrant_attribute_dlg.show()
            self.valve_attribute_dlg.close()
            self.manhole_attribute_dlg.close()
        '''
        self.shape_gid = int(item_text.split(' ')[1])
        self.hydrant_attribute_dlg.show()

        self.hydrant_attribute_dlg.ui.lineEdit_unific_id.clear()

        self.hydrant_attribute_dlg.ui.comboBox_hydrant_type.clear()
        self.hydrant_attribute_dlg.ui.comboBox_hydrant_status.clear()
        self.hydrant_attribute_dlg.ui.comboBox_hydrant_sw.clear()
        self.hydrant_attribute_dlg.ui.comboBox_cvalve_sw.clear()
        self.hydrant_attribute_dlg.ui.comboBox_hydrant_mode.clear()
        

        # 設置下拉選單
        hydrant_type_list = [u'0 地上式單口式', u'1 地上打倒安全式.單口', u'2 地上式雙口式', u'3 地上打倒安全式.雙口', u'4 地下式單口式', u'5 地下式雙口式']
        self.hydrant_attribute_dlg.ui.comboBox_hydrant_type.addItems(hydrant_type_list)
        hydrant_status_list = [u'0 正常', u'1 停用']
        self.hydrant_attribute_dlg.ui.comboBox_hydrant_status.addItems(hydrant_status_list)
        hydrant_sw_list = [u'0 順時針', u'1 逆時針']
        self.hydrant_attribute_dlg.ui.comboBox_hydrant_sw.addItems(hydrant_sw_list)
        cvalve_sw_list = [u'0 OFF', u'1 ON']
        self.hydrant_attribute_dlg.ui.comboBox_cvalve_sw.addItems(cvalve_sw_list)
        hydrant_mode_list = [u'0 非測量', u'1 測量', u'2 合理化調整']
        self.hydrant_attribute_dlg.ui.comboBox_hydrant_mode.addItems(hydrant_mode_list)
        

        # 設置文字輸入框 文字格式
        self.hydrant_attribute_dlg.ui.lineEdit_hydrant_id.setText("")
        self.hydrant_attribute_dlg.ui.lineEdit_hydrant_id.setDisabled(True)
    
        self.hydrant_attribute_dlg.ui.lineEdit_hydrant_model.clear()
        self.hydrant_attribute_dlg.ui.lineEdit_hydrant_pd.clear()
        self.hydrant_attribute_dlg.ui.lineEdit_firebureau_id.clear()
        self.hydrant_attribute_dlg.ui.lineEdit_cvalve_model.clear()		
        self.hydrant_attribute_dlg.ui.lineEdit_bury_date.clear()


        self.hydrant_attribute_dlg.ui.lineEdit_bury_loc.clear()
        self.hydrant_attribute_dlg.ui.lineEdit_proj_name.clear()
        self.hydrant_attribute_dlg.ui.lineEdit_const_unit.clear()
        self.hydrant_attribute_dlg.ui.lineEdit_admin_unit.clear()
        self.hydrant_attribute_dlg.ui.lineEdit_remark.clear()
    
        self.hydrant_attribute_dlg.ui.plainTextEdit_maint_date.clear()
        self.hydrant_attribute_dlg.ui.plainTextEdit_maint_rec.clear()
        self.hydrant_attribute_dlg.ui.listWidget_maint_date.clear()


        # 設置文字輸入框 數字格式
        self.hydrant_attribute_dlg.ui.lineEdit_hydrant_size.clear()
        self.hydrant_attribute_dlg.ui.lineEdit_hydrant_turn.clear()
        self.hydrant_attribute_dlg.ui.lineEdit_cpipe_size.clear()
        self.hydrant_attribute_dlg.ui.lineEdit_outlet_size.clear()
        self.hydrant_attribute_dlg.ui.lineEdit_cvalve_turn.clear()

        self.hydrant_attribute_dlg.ui.lineEdit_bury_depth.setText(u'0000.000')
        self.hydrant_attribute_dlg.ui.lineEdit_pressure.setText(u'0000.000')
        self.hydrant_attribute_dlg.ui.lineEdit_coord_97z.setText(u'0000.000')
        #self.hydrant_attribute_dlg.ui.lineEdit_base_elev.setText(u'0000.000')


        self.hydrant_attribute_dlg.ui.lineEdit_coord_67x.setText(u'00000000.000')
        self.hydrant_attribute_dlg.ui.lineEdit_coord_67y.setText(u'00000000.000')
        self.hydrant_attribute_dlg.ui.lineEdit_coord_97x.setText(u'00000000.000')
        self.hydrant_attribute_dlg.ui.lineEdit_coord_97y.setText(u'00000000.000')
        
        #三支距
        self.hydrant_attribute_dlg.ui.teP1x.setText("")
        self.hydrant_attribute_dlg.ui.teP1y.setText("")
        self.hydrant_attribute_dlg.ui.teP2x.setText("")
        self.hydrant_attribute_dlg.ui.teP2y.setText("")
        self.hydrant_attribute_dlg.ui.teP3x.setText("")
        self.hydrant_attribute_dlg.ui.teP3y.setText("")
        self.hydrant_attribute_dlg.ui.teP1disc.setText("")
        self.hydrant_attribute_dlg.ui.teP2disc.setText("")
        self.hydrant_attribute_dlg.ui.teP3disc.setText("")
        self.hydrant_attribute_dlg.ui.teP1dis.setText("")
        self.hydrant_attribute_dlg.ui.teP2dis.setText("")
        self.hydrant_attribute_dlg.ui.teP3dis.setText("")                   
        self.hydrant_attribute_dlg.ui.cbP1pos.setCurrentIndex(-1)
        self.hydrant_attribute_dlg.ui.cbP2pos.setCurrentIndex(-1)
        self.hydrant_attribute_dlg.ui.cbP3pos.setCurrentIndex(-1)
        txt=u"第一支點  距【】【】公尺" 
        self.hydrant_attribute_dlg.ui.lbl_pin1.setText(txt)
        txt=u"第二支點  距【】【】公尺"
        self.hydrant_attribute_dlg.ui.lbl_pin2.setText(txt)
        txt=u"第三支點  距【】【】公尺"
        self.hydrant_attribute_dlg.ui.lbl_pin3.setText(txt)

        
        
        db_conn = self.get_db_connection()
        query_string = u'SELECT * FROM hydrant WHERE gid={}'.format(self.shape_gid)
        query = db_conn.exec_(query_string)
        if query.isActive():
            while query.next():
                record = query.record()


                #GID
                if record.field('gid').value()!=None:
                    gid_c = unicode(record.field('gid').value())
                    self.hydrant_attribute_dlg.ui.tegid.setText(gid_c)

                
                #UID
                if (record.field('unific_id').value() !=None) and (record.field('unific_id').value() !=''):
                    unific_id_c = unicode(record.field('unific_id').value())
                    self.hydrant_attribute_dlg.ui.lineEdit_unific_id.setText(unific_id_c)
                    self.hydrant_attribute_dlg.ui.teuid.setText(unific_id_c)
                    self.unific_id_c = unicode(record.field('unific_id').value())
                    #self.hydrant_attribute_dlg.ui.btUID.setEnabled(False)            
                else:   
                    self.hydrant_attribute_dlg.ui.lineEdit_unific_id.setText("")     
                    #self.hydrant_attribute_dlg.ui.btUID.setEnabled(True)            
                    #self.hydrant_attribute_dlg.ui.lineEdit_unific_id.setDisabled(True)
                    
                
                #消防栓狀態
                if (record.field('hydrant_status').value() !=None) and (record.field('hydrant_status').value()!=''):
                    self.hydrant_attribute_dlg.ui.comboBox_hydrant_status.setCurrentIndex(int(record.field("hydrant_status").value()))
                else:   
                    self.hydrant_attribute_dlg.ui.comboBox_hydrant_status.setCurrentIndex(-1)     

                
                #測量註記
                if (record.field('hydrant_mode').value() !=None) and (record.field('hydrant_mode').value()!=''):
                    self.hydrant_attribute_dlg.ui.comboBox_hydrant_mode.setCurrentIndex(int(record.field("hydrant_mode").value()))
                else:   
                    self.hydrant_attribute_dlg.ui.comboBox_hydrant_mode.setCurrentIndex(-1)     
        
                #廠牌型號
                if record.field('hydrant_model').value() !=None:
                    hydrant_model_c=unicode(record.field("hydrant_model").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_hydrant_model.setText(hydrant_model_c)
                else:   
                    self.hydrant_attribute_dlg.ui.lineEdit_hydrant_model.setText("")

                #閥類編號             
                if record.field('hydrant_id').value() !=None:
                    hydrant_id_c=unicode(record.field("hydrant_id").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_hydrant_id.setText(hydrant_id_c)
                else:   
                    self.hydrant_attribute_dlg.ui.lineEdit_hydrant_id.setText("")
                    self.hydrant_attribute_dlg.ui.lineEdit_hydrant_id.setDisabled(True)
                
                #舊編號             
                if record.field('hydrant_pd').value() !=None:
                    hydrant_pd_c=unicode(record.field("hydrant_pd").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_hydrant_pd.setText(hydrant_pd_c)
                else:   
                    self.hydrant_attribute_dlg.ui.lineEdit_hydrant_pd.setText("")

                #消防栓轉向            
                if (record.field('hydrant_sw').value() !=None) and (record.field('hydrant_sw').value()!=''):
                    self.hydrant_attribute_dlg.ui.comboBox_hydrant_sw.setCurrentIndex(int(record.field("hydrant_sw").value()))
                else:   
                    self.hydrant_attribute_dlg.ui.comboBox_hydrant_sw.setCurrentIndex(-1)
                
                #消防栓型態             
                if (record.field('hydrant_type').value() !=None) and (record.field('hydrant_type')!=''):
                    self.hydrant_attribute_dlg.ui.comboBox_hydrant_type.setCurrentIndex(int(record.field("hydrant_type").value()))
                else:   
                    self.hydrant_attribute_dlg.ui.comboBox_hydrant_type.setCurrentIndex(-1)
                
                #口徑
                if record.field('hydrant_size').value() !=None:
                    hydrant_size_c=unicode(int(record.field("hydrant_size").value()))
                    self.hydrant_attribute_dlg.ui.lineEdit_hydrant_size.setText(hydrant_size_c)      
                else:   
                    self.hydrant_attribute_dlg.ui.lineEdit_hydrant_size.setText("")     
                
                #轉數                 
                if record.field('hydrant_turn').value() !=None:
                    hydrant_turn_c=unicode(int(record.field("hydrant_turn").value()))
                    self.hydrant_attribute_dlg.ui.lineEdit_hydrant_turn.setText(hydrant_turn_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_hydrant_turn.setText("")         

                #連接管口徑
                if record.field('cpipe_size').value() !=None:
                    cpipe_size_c=unicode(int(record.field("cpipe_size").value()))
                    self.hydrant_attribute_dlg.ui.lineEdit_cpipe_size.setText(cpipe_size_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_cpipe_size.setText('0')

                #出水口口徑                
                if record.field('outlet_size').value() !=None:
                    outlet_size_c=unicode(int(record.field("outlet_size").value()))
                    self.hydrant_attribute_dlg.ui.lineEdit_outlet_size.setText(outlet_size_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_outlet_size.setText('0')                
                
                #連接管廠牌
                if record.field('cvalve_model').value() !=None:
                    cvalve_model_c=unicode(record.field("cvalve_model").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_cvalve_model.setText(cvalve_model_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_cvalve_model.setText('')                
                
                #連接管轉向
                if (record.field('cvalve_sw').value() !=None) and (record.field('cvalve_sw').value()!=''):
                    self.hydrant_attribute_dlg.ui.comboBox_cvalve_sw.setCurrentIndex(int(record.field("cvalve_sw").value()))
                else:   
                    self.hydrant_attribute_dlg.ui.comboBox_cvalve_sw.setCurrentIndex(-1)
                
                #連接管轉數
                if record.field('cvalve_turn').value() !=None:
                    cvalve_turn_c=unicode(record.field("cvalve_turn").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_cvalve_turn.setText(cvalve_turn_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_cvalve_turn.setText('0')                
            
                #埋設位置
                if record.field('bury_loc').value() !=None:
                    bury_loc_c=unicode(record.field("bury_loc").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_bury_loc.setText(bury_loc_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_bury_loc.setText("")

                #埋設深度
                if record.field('bury_depth').value() !=None:
                    bury_depth_c=unicode(record.field("bury_depth").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_bury_depth.setText(bury_depth_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_bury_depth.setText("")

                #埋設日期
                if record.field('bury_date').value() !=None:
                    bury_date_c=unicode(record.field("bury_date").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_bury_date.setText(bury_date_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_bury_date.setText("")

                '''
                #資料來自 巡查紀錄 
                #養護及檢查日期
                query_string = u"SELECT * FROM inspect_hydrant where unific_id ='"+unific_id_c+"' order by insdate DESC"
                result2 = QSqlQuery(db_twwater)
                result2 = db_twwater.exec_(query_string)
                while result2.next():
                    record = result2.record()
                    self.hydrant_attribute_dlg.ui.listWidget_maint_date.addItem(u"%s - %s" % (record.field('insdate').value(),record.field('status').value()))
                '''

                #所有者
                if record.field('admin_unit').value() !=None:
                    admin_unit_c=unicode(record.field("admin_unit").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_admin_unit.setText(admin_unit_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_admin_unit.setText("")


                #水壓
                if record.field('pressure').value() !=None:
                    pressure_c=unicode(record.field("pressure").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_pressure.setText(pressure_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_pressure.setText("")


                #監造單位
                if record.field('const_unit').value() !=None:
                    const_unit_c=unicode(record.field("const_unit").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_const_unit.setText(const_unit_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_const_unit.setText("")


                #工程名稱
                if record.field('proj_name').value() !=None:
                    proj_name_c=unicode(record.field("proj_name").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_proj_name.setText(proj_name_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_proj_name.setText("")


                #註記說明
                if record.field('remark').value() !=None:
                    remark_c=unicode(record.field("remark").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_remark.setText(remark_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_remark.setText("")
                

                #測量註記
                '''
                if record.field('hydrant_mode').value() !=None:
                    self.hydrant_attribute_dlg.ui.comboBox_hydrant_mode.setCurrentIndex(int(record.field("hydrant_mode")))
                else:
                    self.hydrant_attribute_dlg.ui.comboBox_hydrant_mode.setCurrentIndex(-1)
                '''


                #地盤高程
                if record.field('coord_97z').value() !=None:
                    coord_97z_c=unicode(record.field("coord_97z").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_coord_97z.setText(coord_97z_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_coord_97z.setText('0.0')


                #地盤高
                '''
                if record.field('base_elev').value() !=None:
                    base_elev_c=unicode(record.field("base_elev").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_base_elev.setText(base_elev_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_base_elev.setText('0.0')
                '''
                
                if record.field('coord_67x').value() !=None:
                    coord_67x_c=unicode(record.field("coord_67x").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_coord_67x.setText(coord_67x_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_coord_67x.setText('0.0')
                

                if record.field('coord_67y').value() !=None:
                    coord_67y_c=unicode(record.field("coord_67y").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_coord_67y.setText(coord_67y_c)
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_coord_67y.setText('0.0')
                

                if record.field('coord_97x').value() !=None:
                    coord_97x_c=unicode(record.field("coord_97x").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_coord_97x.setText(coord_97x_c)
                    self.hydrant_attribute_dlg.ui.teVx.setText(coord_97x_c)
                    self.featX = coord_97x_c
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_coord_97x.setText('0.0')


                if record.field('coord_97y').value() !=None:
                    coord_97y_c=unicode(record.field("coord_97y").value())
                    self.hydrant_attribute_dlg.ui.lineEdit_coord_97y.setText(coord_97y_c)
                    self.hydrant_attribute_dlg.ui.teVy.setText(coord_97x_c)
                    self.featY = coord_97y_c
                else:
                    self.hydrant_attribute_dlg.ui.lineEdit_coord_97y.setText('0.0')
        
            #取出三支距屬性----------
        query_string = u"SELECT * FROM surveytie WHERE unific_id='%s'" %str(self.unific_id_c)
        db_conn = self.get_db_connection()
        query = db_conn.exec_(query_string)
        if query.isActive():
            while query.next():
                record = query.record()

                self.hydrant_attribute_dlg.ui.teP1x.setText(str(record.field('p1_x').value()))
                self.hydrant_attribute_dlg.ui.teP1y.setText(str(record.field('p1_y').value()))
                self.hydrant_attribute_dlg.ui.teP2x.setText(str(record.field('p2_x').value()))
                self.hydrant_attribute_dlg.ui.teP2y.setText(str(record.field('p2_y').value()))
                self.hydrant_attribute_dlg.ui.teP3x.setText(str(record.field('p3_x').value()))
                self.hydrant_attribute_dlg.ui.teP3y.setText(str(record.field('p3_y').value()))
                if record.field('p1_desc').value()!=NULL:
                    self.hydrant_attribute_dlg.ui.teP1disc.setText(record.field('p1_desc').value())
                if record.field('p2_desc').value()!=NULL:
                    self.hydrant_attribute_dlg.ui.teP2disc.setText(record.field('p2_desc').value())
                if record.field('p3_desc').value()!=NULL:
                    self.hydrant_attribute_dlg.ui.teP3disc.setText(record.field('p3_desc').value())
                self.hydrant_attribute_dlg.ui.teP1dis.setText(str(record.field('p1_dist').value()))
                self.hydrant_attribute_dlg.ui.teP2dis.setText(str(record.field('p2_dist').value()))
                self.hydrant_attribute_dlg.ui.teP3dis.setText(str(record.field('p3_dist').value())) 
                '''                  
                P1	電力桿
                P2	電信桿
                M1	電力人孔
                M2	電信人孔
                B1	電信箱座
                SL	路燈
                TL	交通號誌
                D1	門柱
                HC	屋角
                BD	建物
                TR	三角點
                BM	水準點
                T1	變電箱座
                T2	變壓箱座
                RI	安全島
                WT	水池
                BW	板牆
                WA	圍牆
                RS	路邊
                WN	鐵絲網
                GP	路標
                OT  其他
                '''
                cbP1pos_index=-1
                cbP2pos_index=-1
                cbP3pos_index=-1
                if record.field('p1_type').value()!=NULL:
                    if record.field('p1_type').value()=='P1':
                        cbP1pos_index=1
                    elif record.field('p1_type').value()=='P2':
                        cbP1pos_index=2
                    elif record.field('p1_type').value()=='M1':
                        cbP1pos_index=3
                    elif record.field('p1_type').value()=='M2':
                        cbP1pos_index=4
                    elif record.field('p1_type').value()=='B1':
                        cbP1pos_index=5
                    elif record.field('p1_type').value()=='SL':
                        cbP1pos_index=6
                    elif record.field('p1_type').value()=='TL':
                        cbP1pos_index=7
                    elif record.field('p1_type').value()=='D1':
                        cbP1pos_index=8
                    elif record.field('p1_type').value()=='HC':
                        cbP1pos_index=9
                    elif record.field('p1_type').value()=='BD':
                        cbP1pos_index=10
                    elif record.field('p1_type').value()=='TR':
                        cbP1pos_index=11
                    elif record.field('p1_type').value()=='BM':
                        cbP1pos_index=12
                    elif record.field('p1_type').value()=='T1':
                        cbP1pos_index=13
                    elif record.field('p1_type').value()=='T2':
                        cbP1pos_index=14
                    elif record.field('p1_type').value()=='RI':
                        cbP1pos_index=15
                    elif record.field('p1_type').value()=='WT':
                        cbP1pos_index=16
                    elif record.field('p1_type').value()=='BW':
                        cbP1pos_index=17
                    elif record.field('p1_type').value()=='WA':
                        cbP1pos_index=18
                    elif record.field('p1_type').value()=='RS':
                        cbP1pos_index=19
                    elif record.field('p1_type').value()=='WN':
                        cbP1pos_index=20
                    elif record.field('p1_type').value()=='GP':
                        cbP1pos_index=21
                    elif record.field('p1_type').value()=='OT':
                        cbP1pos_index=22
                    self.hydrant_attribute_dlg.ui.cbP1pos.setCurrentIndex(cbP1pos_index)
                
                if record.field('p2_type').value()!=NULL:
                    if record.field('p2_type').value()=='P1':
                        cbP2pos_index=1
                    elif record.field('p2_type').value()=='P2':
                        cbP2pos_index=2
                    elif record.field('p2_type').value()=='M1':
                        cbP2pos_index=3
                    elif record.field('p2_type').value()=='M2':
                        cbP2pos_index=4
                    elif record.field('p2_type').value()=='B1':
                        cbP2pos_index=5
                    elif record.field('p2_type').value()=='SL':
                        cbP2pos_index=6
                    elif record.field('p2_type').value()=='TL':
                        cbP2pos_index=7
                    elif record.field('p2_type').value()=='D1':
                        cbP2pos_index=8
                    elif record.field('p2_type').value()=='HC':
                        cbP2pos_index=9
                    elif record.field('p2_type').value()=='BD':
                        cbP2pos_index=10
                    elif record.field('p2_type').value()=='TR':
                        cbP2pos_index=11
                    elif record.field('p2_type').value()=='BM':
                        cbP2pos_index=12
                    elif record.field('p2_type').value()=='T1':
                        cbP2pos_index=13
                    elif record.field('p2_type').value()=='T2':
                        cbP2pos_index=14
                    elif record.field('p2_type').value()=='RI':
                        cbP2pos_index=15
                    elif record.field('p2_type').value()=='WT':
                        cbP2pos_index=16
                    elif record.field('p2_type').value()=='BW':
                        cbP2pos_index=17
                    elif record.field('p2_type').value()=='WA':
                        cbP2pos_index=18
                    elif record.field('p2_type').value()=='RS':
                        cbP2pos_index=19
                    elif record.field('p2_type').value()=='WN':
                        cbP2pos_index=20
                    elif record.field('p2_type').value()=='GP':
                        cbP2pos_index=21
                    elif record.field('p2_type').value()=='OT':
                        cbP2pos_index=22
                    self.hydrant_attribute_dlg.ui.cbP2pos.setCurrentIndex(cbP2pos_index)
                
                if record.field('p3_type').value()!=NULL:
                    if record.field('p3_type').value()=='P1':
                        cbP3pos_index=1
                    elif record.field('p3_type').value()=='P2':
                        cbP3pos_index=2
                    elif record.field('p3_type').value()=='M1':
                        cbP3pos_index=3
                    elif record.field('p3_type').value()=='M2':
                        cbP3pos_index=4
                    elif record.field('p3_type').value()=='B1':
                        cbP3pos_index=5
                    elif record.field('p3_type').value()=='SL':
                        cbP3pos_index=6
                    elif record.field('p3_type').value()=='TL':
                        cbP3pos_index=7
                    elif record.field('p3_type').value()=='D1':
                        cbP3pos_index=8
                    elif record.field('p3_type').value()=='HC':
                        cbP3pos_index=9
                    elif record.field('p3_type').value()=='BD':
                        cbP3pos_index=10
                    elif record.field('p3_type').value()=='TR':
                        cbP3pos_index=11
                    elif record.field('p3_type').value()=='BM':
                        cbP3pos_index=12
                    elif record.field('p3_type').value()=='T1':
                        cbP3pos_index=13
                    elif record.field('p3_type').value()=='T2':
                        cbP3pos_index=14
                    elif record.field('p3_type').value()=='RI':
                        cbP3pos_index=15
                    elif record.field('p3_type').value()=='WT':
                        cbP3pos_index=16
                    elif record.field('p3_type').value()=='BW':
                        cbP3pos_index=17
                    elif record.field('p3_type').value()=='WA':
                        cbP3pos_index=18
                    elif record.field('p3_type').value()=='RS':
                        cbP3pos_index=19
                    elif record.field('p3_type').value()=='WN':
                        cbP3pos_index=20
                    elif record.field('p3_type').value()=='GP':
                        cbP3pos_index=21
                    elif record.field('p3_type').value()=='OT':
                        cbP3pos_index=22
                    self.hydrant_attribute_dlg.ui.cbP3pos.setCurrentIndex(cbP3pos_index)
                    
                txt=u"第一支點  距【%s%s】【%s】公尺" % (self.hydrant_attribute_dlg.ui.teP1disc.toPlainText(),self.hydrant_attribute_dlg.ui.cbP1pos.currentText(),self.hydrant_attribute_dlg.ui.teP1dis.toPlainText())
                self.hydrant_attribute_dlg.ui.lbl_pin1.setText(txt)
                txt=u"第二支點  距【%s%s】【%s】公尺" % (self.hydrant_attribute_dlg.ui.teP2disc.toPlainText(),self.hydrant_attribute_dlg.ui.cbP2pos.currentText(),self.hydrant_attribute_dlg.ui.teP2dis.toPlainText())
                self.hydrant_attribute_dlg.ui.lbl_pin2.setText(txt)
                txt=u"第三支點  距【%s%s】【%s】公尺" % (self.hydrant_attribute_dlg.ui.teP3disc.toPlainText(),self.hydrant_attribute_dlg.ui.cbP3pos.currentText(),self.hydrant_attribute_dlg.ui.teP3dis.toPlainText())
                self.hydrant_attribute_dlg.ui.lbl_pin3.setText(txt)

    def hydrant_attribute_ok(self):

        unific_id = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_unific_id.text() + u"'"
        hydrant_type = u"'" + self.hydrant_attribute_dlg.ui.comboBox_hydrant_type.currentText().split(' ')[0] + u"'"
        hydrant_status = u"'" + self.hydrant_attribute_dlg.ui.comboBox_hydrant_status.currentText().split(' ')[0] + u"'"
        hydrant_sw = u"'" + self.hydrant_attribute_dlg.ui.comboBox_hydrant_sw.currentText().split(' ')[0] + u"'"
        cvalve_sw = u"'" + self.hydrant_attribute_dlg.ui.comboBox_cvalve_sw.currentText().split(' ')[0] + u"'"
        hydrant_mode = u"'" + self.hydrant_attribute_dlg.ui.comboBox_hydrant_mode.currentText().split(' ')[0] + u"'"

        # 處理文字 lineEdit
        hydrant_id = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_hydrant_id.text() + u"'"

        hydrant_model = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_hydrant_model.text() + u"'"
        hydrant_pd = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_hydrant_pd.text() + u"'"
        firebureau_id = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_firebureau_id.text() + u"'"
        cvalve_model = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_cvalve_model.text() + u"'"
        bury_date = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_bury_date.text() + u"'"
    
        bury_loc = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_bury_loc.text() + u"'"
        proj_name = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_proj_name.text() + u"'"
        const_unit = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_const_unit.text() + u"'"
        admin_unit = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_admin_unit.text() + u"'"
        remark = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_remark.text() + u"'"

        maint_date = u"'" + self.hydrant_attribute_dlg.ui.plainTextEdit_maint_date.toPlainText() + u"'"
        maint_rec = u"'" + self.hydrant_attribute_dlg.ui.plainTextEdit_maint_rec.toPlainText() + u"'"

        # 處理數字 lineEdit ，避免 數字 欄位，以空值(只有一個預設小數點)寫入 資料庫，型態不符所發生之錯誤

        if len(self.hydrant_attribute_dlg.ui.lineEdit_hydrant_size.text()) > 1:
            hydrant_size = int(self.hydrant_attribute_dlg.ui.lineEdit_hydrant_size.text())
        else:
            hydrant_size = 0

        if len(self.hydrant_attribute_dlg.ui.lineEdit_hydrant_turn.text()) > 1:
            hydrant_turn = int(self.hydrant_attribute_dlg.ui.lineEdit_hydrant_turn.text())
        else:
            hydrant_turn = 0

        if len(self.hydrant_attribute_dlg.ui.lineEdit_cpipe_size.text()) > 1:
            cpipe_size = int(self.hydrant_attribute_dlg.ui.lineEdit_cpipe_size.text())
        else:
            cpipe_size = 0

        if len(self.hydrant_attribute_dlg.ui.lineEdit_outlet_size.text()) > 1:
            outlet_size = int(self.hydrant_attribute_dlg.ui.lineEdit_outlet_size.text())
        else:
            outlet_size = 0
            
        if len(self.hydrant_attribute_dlg.ui.lineEdit_cvalve_turn.text()) > 1:
            cvalve_turn = int(self.hydrant_attribute_dlg.ui.lineEdit_cvalve_turn.text())
        else:
            cvalve_turn = 0
        
        if len(self.hydrant_attribute_dlg.ui.lineEdit_bury_depth.text()) > 1:
            bury_depth = float(self.hydrant_attribute_dlg.ui.lineEdit_bury_depth.text())
        else:
            bury_depth = 0.0

        if len(self.hydrant_attribute_dlg.ui.lineEdit_pressure.text()) > 1:
            pressure = float(self.hydrant_attribute_dlg.ui.lineEdit_pressure.text())
        else:
            pressure = 0.0

        #if len(self.hydrant_attribute_dlg.ui.lineEdit_base_elev.text()) > 1:
        #   base_elev = float(self.hydrant_attribute_dlg.ui.lineEdit_base_elev.text())
        #else:
        #   base_elev = 0.0

        if len(self.hydrant_attribute_dlg.ui.lineEdit_coord_97z.text()) > 1:
            coord_97z = float(self.hydrant_attribute_dlg.ui.lineEdit_coord_97z.text())
        else:
            coord_97z = 0.0

        if len(self.hydrant_attribute_dlg.ui.lineEdit_coord_67x.text()) > 1:
            coord_67x = float(self.hydrant_attribute_dlg.ui.lineEdit_coord_67x.text())
        else:
            coord_67x = 0.0

        if len(self.hydrant_attribute_dlg.ui.lineEdit_coord_67y.text()) > 1:
            coord_67y = float(self.hydrant_attribute_dlg.ui.lineEdit_coord_67y.text())
        else:
            coord_67y = 0.0

        if len(self.hydrant_attribute_dlg.ui.lineEdit_coord_97x.text()) > 1:
            coord_97x = float(self.hydrant_attribute_dlg.ui.lineEdit_coord_97x.text())
        else:
            coord_97x = 0.0

        if len(self.hydrant_attribute_dlg.ui.lineEdit_coord_97y.text()) > 1:
            coord_97y = float(self.hydrant_attribute_dlg.ui.lineEdit_coord_97y.text())
        else:
            coord_97y = 0.0


        db_conn = self.get_db_connection()

        query_string = u"UPDATE hydrant set unific_id={}, hydrant_type={}, hydrant_status={}, hydrant_sw={}, cvalve_sw={}, hydrant_mode={}, hydrant_model={}, hydrant_pd={}, " \
        " firebureau_id={}, cvalve_model={},bury_date={}, bury_loc={}, proj_name={}, const_unit={}, admin_unit={}, remark={}, maint_date={}, maint_rec={}, " \
        "hydrant_size={}, hydrant_turn={}, cpipe_size={}, outlet_size={}, cvalve_turn={}, bury_depth={}, pressure={}, coord_97z={}," \
        "coord_67x={}, coord_67y={}, coord_97x={}, coord_97y={} where gid={}" \
        ''.format(unific_id, hydrant_type, hydrant_status, hydrant_sw, cvalve_sw, hydrant_mode, hydrant_model, hydrant_pd, firebureau_id, cvalve_model, bury_date, \
        bury_loc, proj_name, const_unit, admin_unit, remark, maint_date, maint_rec,hydrant_size, hydrant_turn, cpipe_size, outlet_size, cvalve_turn, \
        bury_depth, pressure, coord_97z, coord_67x, coord_67y, coord_97x, coord_97y, self.shape_gid) 
        

        db_conn = self.get_db_connection()
        query = db_conn.exec_(query_string)
        # 檢查執行的 query 是否為有效!
        if query.isActive():
            self.hydrant_attribute_dlg.close()
            query.clear()
            self.iface.mapCanvas().refresh()
            QMessageBox.information(self.iface.mainWindow(), u'修改消防栓', u'資料修改完成!')
        else:
            QMessageBox.warning(self.iface.mainWindow(), u'修改消防栓', u'資料庫寫入失敗!')
        # 關閉資料庫連線
        db_conn.close()
        

#======================================================================================#
#======================================================================================#
#======================================================================================#

    # 新增閥類 - 點選「取消」按鈕，關閉對話框
    def valve_attribute_close(self):

        self.valve_attribute_dlg.close()
        self.canvas.refresh()    

    # 人手孔 - 點選「取消」按鈕，關閉對話框
    def manhole_attribute_close(self):

        self.manhole_attribute_dlg.close()
        self.canvas.refresh()


    # 消防栓 - 點選「取消」按鈕，關閉對話框
    def hydrant_attribute_close(self):

        self.hydrant_attribute_dlg.close()
        self.canvas.refresh()   


    #-------------------------------------------------------
    #             QTextEdit 事件
    #--------------------------------------------------------
    def cbp1posOnChange(self):    
        item_text = self.pick_features_dlg.ui.listWidget_pick.currentItem().text()

        if item_text.split(' ')[0] == u'閥':
            txt=u"第一支點  距【%s%s】【%s】公尺" % (self.valve_attribute_dlg.ui.teP1disc.toPlainText(),self.valve_attribute_dlg.ui.cbP1pos.currentText(),self.valve_attribute_dlg.ui.teP1dis.toPlainText())
            self.valve_attribute_dlg.ui.lbl_pin1.setText(txt)
        elif item_text.split(' ')[0] == u'消防栓':  
            txt=u"第一支點  距【%s%s】【%s】公尺" % (self.hydrant_attribute_dlg.ui.teP1disc.toPlainText(),self.hydrant_attribute_dlg.ui.cbP1pos.currentText(),self.hydrant_attribute_dlg.ui.teP1dis.toPlainText())
            self.hydrant_attribute_dlg.ui.lbl_pin1.setText(txt)
        elif item_text.split(' ')[0] == u'人手孔':  
            txt=u"第一支點  距【%s%s】【%s】公尺" % (self.manhole_attribute_dlg.ui.teP1disc.toPlainText(),self.manhole_attribute_dlg.ui.cbP1pos.currentText(),self.manhole_attribute_dlg.ui.teP1dis.toPlainText())
            self.manhole_attribute_dlg.ui.lbl_pin1.setText(txt)
        db_conn = self.get_db_connection()
        query_string = u"update surveytie_p set textstring='"+txt+"'where gid=1"
        query = db_conn.exec_(query_string)
        self.canvas.refresh()          

    def cbp2posOnChange(self):    
        item_text = self.pick_features_dlg.ui.listWidget_pick.currentItem().text()

        if item_text.split(' ')[0] == u'閥':
            txt=u"第二支點  距【%s%s】【%s】公尺" % (self.valve_attribute_dlg.ui.teP2disc.toPlainText(),self.valve_attribute_dlg.ui.cbP2pos.currentText(),self.valve_attribute_dlg.ui.teP2dis.toPlainText())
            self.valve_attribute_dlg.ui.lbl_pin2.setText(txt)
        elif item_text.split(' ')[0] == u'消防栓':  
            txt=u"第二支點  距【%s%s】【%s】公尺" % (self.hydrant_attribute_dlg.ui.teP2disc.toPlainText(),self.hydrant_attribute_dlg.ui.cbP2pos.currentText(),self.hydrant_attribute_dlg.ui.teP2dis.toPlainText())
            self.hydrant_attribute_dlg.ui.lbl_pin2.setText(txt)
        elif item_text.split(' ')[0] == u'人手孔':  
            txt=u"第二支點  距【%s%s】【%s】公尺" % (self.manhole_attribute_dlg.ui.teP2disc.toPlainText(),self.manhole_attribute_dlg.ui.cbP2pos.currentText(),self.manhole_attribute_dlg.ui.teP2dis.toPlainText())
            self.manhole_attribute_dlg.ui.lbl_pin2.setText(txt)
        db_conn = self.get_db_connection()
        query_string = u"update surveytie_p set textstring='"+txt+"'where gid=2"
        query = db_conn.exec_(query_string)
        self.canvas.refresh()            
        
        
    def cbp3posOnChange(self): 
        item_text = self.pick_features_dlg.ui.listWidget_pick.currentItem().text()

        if item_text.split(' ')[0] == u'閥':
            txt=u"第三支點  距【%s%s】【%s】公尺" % (self.valve_attribute_dlg.ui.teP3disc.toPlainText(),self.valve_attribute_dlg.ui.cbP3pos.currentText(),self.valve_attribute_dlg.ui.teP3dis.toPlainText())
            self.valve_attribute_dlg.ui.lbl_pin3.setText(txt)
        elif item_text.split(' ')[0] == u'消防栓':  
            txt=u"第三支點  距【%s%s】【%s】公尺" % (self.hydrant_attribute_dlg.ui.teP3disc.toPlainText(),self.hydrant_attribute_dlg.ui.cbP3pos.currentText(),self.hydrant_attribute_dlg.ui.teP3dis.toPlainText())
            self.hydrant_attribute_dlg.ui.lbl_pin3.setText(txt)
        elif item_text.split(' ')[0] == u'人手孔':  
            txt=u"第三支點  距【%s%s】【%s】公尺" % (self.manhole_attribute_dlg.ui.teP3disc.toPlainText(),self.manhole_attribute_dlg.ui.cbP3pos.currentText(),self.manhole_attribute_dlg.ui.teP3dis.toPlainText())
            self.manhole_attribute_dlg.ui.lbl_pin3.setText(txt)
        db_conn = self.get_db_connection()
        query_string = u"update surveytie_p set textstring='"+txt+"'where gid=3"
        query = db_conn.exec_(query_string)
        self.canvas.refresh()       

    def tep1discOnChange(self):
        item_text = self.pick_features_dlg.ui.listWidget_pick.currentItem().text()

        if item_text.split(' ')[0] == u'閥':
            txt=u"第一支點  距【%s%s】【%s】公尺" % (self.valve_attribute_dlg.ui.teP1disc.toPlainText(),self.valve_attribute_dlg.ui.cbP1pos.currentText(),self.valve_attribute_dlg.ui.teP1dis.toPlainText())
            self.valve_attribute_dlg.ui.lbl_pin1.setText(txt)
        elif item_text.split(' ')[0] == u'消防栓':  
            txt=u"第一支點  距【%s%s】【%s】公尺" % (self.hydrant_attribute_dlg.ui.teP1disc.toPlainText(),self.hydrant_attribute_dlg.ui.cbP1pos.currentText(),self.hydrant_attribute_dlg.ui.teP1dis.toPlainText())
            self.hydrant_attribute_dlg.ui.lbl_pin1.setText(txt)
        elif item_text.split(' ')[0] == u'人手孔':  
            txt=u"第一支點  距【%s%s】【%s】公尺" % (self.manhole_attribute_dlg.ui.teP1disc.toPlainText(),self.manhole_attribute_dlg.ui.cbP1pos.currentText(),self.manhole_attribute_dlg.ui.teP1dis.toPlainText())
            self.manhole_attribute_dlg.ui.lbl_pin1.setText(txt)

    def tep2discOnChange(self):
        item_text = self.pick_features_dlg.ui.listWidget_pick.currentItem().text()

        if item_text.split(' ')[0] == u'閥':
            txt=u"第二支點  距【%s%s】【%s】公尺" % (self.valve_attribute_dlg.ui.teP2disc.toPlainText(),self.valve_attribute_dlg.ui.cbP2pos.currentText(),self.valve_attribute_dlg.ui.teP2dis.toPlainText())
            self.valve_attribute_dlg.ui.lbl_pin2.setText(txt)
        elif item_text.split(' ')[0] == u'消防栓':  
            txt=u"第二支點  距【%s%s】【%s】公尺" % (self.hydrant_attribute_dlg.ui.teP2disc.toPlainText(),self.hydrant_attribute_dlg.ui.cbP2pos.currentText(),self.hydrant_attribute_dlg.ui.teP2dis.toPlainText())
            self.hydrant_attribute_dlg.ui.lbl_pin2.setText(txt)
        elif item_text.split(' ')[0] == u'人手孔':  
            txt=u"第二支點  距【%s%s】【%s】公尺" % (self.manhole_attribute_dlg.ui.teP2disc.toPlainText(),self.manhole_attribute_dlg.ui.cbP2pos.currentText(),self.manhole_attribute_dlg.ui.teP2dis.toPlainText())
            self.manhole_attribute_dlg.ui.lbl_pin2.setText(txt)

    def tep3discOnChange(self):
        item_text = self.pick_features_dlg.ui.listWidget_pick.currentItem().text()

        if item_text.split(' ')[0] == u'閥':
            txt=u"第三支點  距【%s%s】【%s】公尺" % (self.valve_attribute_dlg.ui.teP3disc.toPlainText(),self.valve_attribute_dlg.ui.cbP3pos.currentText(),self.valve_attribute_dlg.ui.teP3dis.toPlainText())
            self.valve_attribute_dlg.ui.lbl_pin3.setText(txt)
        elif item_text.split(' ')[0] == u'消防栓':  
            txt=u"第三支點  距【%s%s】【%s】公尺" % (self.hydrant_attribute_dlg.ui.teP3disc.toPlainText(),self.hydrant_attribute_dlg.ui.cbP3pos.currentText(),self.hydrant_attribute_dlg.ui.teP3dis.toPlainText())
            self.hydrant_attribute_dlg.ui.lbl_pin3.setText(txt)
        elif item_text.split(' ')[0] == u'人手孔':  
            txt=u"第三支點  距【%s%s】【%s】公尺" % (self.manhole_attribute_dlg.ui.teP3disc.toPlainText(),self.manhole_attribute_dlg.ui.cbP3pos.currentText(),self.manhole_attribute_dlg.ui.teP3dis.toPlainText())
            self.manhole_attribute_dlg.ui.lbl_pin3.setText(txt)
    

    #支距屬性儲存
    def pin_save(self):
        print 'valve_attribute -> pin_save'
        item_text = self.pick_features_dlg.ui.listWidget_pick.currentItem().text()


        # 處理 comboBox 的欄位
        if item_text.split(' ')[0] == u'閥': 
            pidx = self.valve_attribute_dlg.ui.cbP1pos.currentIndex()
            print item_text.split(' ')[0]
            p1_type=''
            if pidx==1:
                p1_type='P1'
            elif pidx==2:
                p1_type='P2'
            elif pidx==3:
                p1_type='M1'
            elif pidx==4:
                p1_type='M2'
            elif pidx==5:
                p1_type='B1'
            elif pidx==6:
                p1_type='SL'
            elif pidx==7:
                p1_type='TL'
            elif pidx==8:
                p1_type='D1'
            elif pidx==9:
                p1_type='HC'
            elif pidx==10:
                p1_type='BD'
            elif pidx==11:
                p1_type='TR'
            elif pidx==12:
                p1_type='BM'
            elif pidx==13:
                p1_type='T1'
            elif pidx==14:
                p1_type='T2'
            elif pidx==15:
                p1_type='RI'
            elif pidx==16:
                p1_type='WT'
            elif pidx==17:
                p1_type='BW'
            elif pidx==18:
                p1_type='WA'
            elif pidx==19:
                p1_type='RS'
            elif pidx==20:
                p1_type='WN'
            elif pidx==21:
                p1_type='GP'
            elif pidx==22:
                p1_type='OT'

            pidx = self.valve_attribute_dlg.ui.cbP2pos.currentIndex()
            p2_type=''
            if pidx==1:
                p2_type='P1'
            elif pidx==2:
                p2_type='P2'
            elif pidx==3:
                p2_type='M1'
            elif pidx==4:
                p2_type='M2'
            elif pidx==5:
                p2_type='B1'
            elif pidx==6:
                p2_type='SL'
            elif pidx==7:
                p2_type='TL'
            elif pidx==8:
                p2_type='D1'
            elif pidx==9:
                p2_type='HC'
            elif pidx==10:
                p2_type='BD'
            elif pidx==11:
                p2_type='TR'
            elif pidx==12:
                p2_type='BM'
            elif pidx==13:
                p2_type='T1'
            elif pidx==14:
                p2_type='T2'
            elif pidx==15:
                p2_type='RI'
            elif pidx==16:
                p2_type='WT'
            elif pidx==17:
                p2_type='BW'
            elif pidx==18:
                p2_type='WA'
            elif pidx==19:
                p2_type='RS'
            elif pidx==20:
                p2_type='WN'
            elif pidx==21:
                p2_type='GP'
            elif pidx==22:
                p2_type='OT'

            pidx = self.valve_attribute_dlg.ui.cbP3pos.currentIndex()
            p3_type=''
            if pidx==1:
                p3_type='P1'
            elif pidx==2:
                p3_type='P2'
            elif pidx==3:
                p3_type='M1'
            elif pidx==4:
                p3_type='M2'
            elif pidx==5:
                p3_type='B1'
            elif pidx==6:
                p3_type='SL'
            elif pidx==7:
                p3_type='TL'
            elif pidx==8:
                p3_type='D1'
            elif pidx==9:
                p3_type='HC'
            elif pidx==10:
                p3_type='BD'
            elif pidx==11:
                p3_type='TR'
            elif pidx==12:
                p3_type='BM'
            elif pidx==13:
                p3_type='T1'
            elif pidx==14:
                p3_type='T2'
            elif pidx==15:
                p3_type='RI'
            elif pidx==16:
                p3_type='WT'
            elif pidx==17:
                p3_type='BW'
            elif pidx==18:
                p3_type='WA'
            elif pidx==19:
                p3_type='RS'
            elif pidx==20:
                p3_type='WN'
            elif pidx==21:
                p3_type='GP'
            elif pidx==22:
                p3_type='OT'
            #p1_type = u"'" + str(self.valve_attribute_dlg.ui.cbP1pos.currentIndex()) + u"'"
            #p2_type = u"'" + str(self.valve_attribute_dlg.ui.cbP2pos.currentIndex()) + u"'"
            #p3_type = u"'" + str(self.valve_attribute_dlg.ui.cbP3pos.currentIndex()) + u"'"
            p1_type = u"'" + p1_type + u"'"
            p2_type = u"'" + p2_type + u"'"
            p3_type = u"'" + p3_type + u"'"

            # 處理文字 lineEdit
            unific_id = u"'" + self.valve_attribute_dlg.ui.lineEdit_unific_id.text() + u"'"
            p1_desc = u"'" + self.valve_attribute_dlg.ui.teP1disc.toPlainText() + u"'"
            p2_desc = u"'" + self.valve_attribute_dlg.ui.teP2disc.toPlainText() + u"'"
            p3_desc = u"'" + self.valve_attribute_dlg.ui.teP3disc.toPlainText() + u"'"

            # 處理數字 lineEdit ，避免 數字 欄位，以空值(只有一個預設小數點)寫入 資料庫，型態不符所發生之錯誤
            if self.valve_attribute_dlg.ui.teP1x.toPlainText()!="":
                p1_x = float(self.valve_attribute_dlg.ui.teP1x.toPlainText())
            else:
                p1_x = 0.0

            if self.valve_attribute_dlg.ui.teP1y.toPlainText()!="":
                p1_y = float(self.valve_attribute_dlg.ui.teP1y.toPlainText())
            else:
                p1_y = 0.0

            if self.valve_attribute_dlg.ui.teP2x.toPlainText()!="":
                p2_x = float(self.valve_attribute_dlg.ui.teP2x.toPlainText())
            else:
                p2_x = 0.0

            if self.valve_attribute_dlg.ui.teP2y.toPlainText()!="":
                p2_y = float(self.valve_attribute_dlg.ui.teP2y.toPlainText())
            else:
                p2_y = 0.0
        
            if self.valve_attribute_dlg.ui.teP3x.toPlainText()!="":
                p3_x = float(self.valve_attribute_dlg.ui.teP3x.toPlainText())
            else:
                p3_x = 0.0

            if self.valve_attribute_dlg.ui.teP3y.toPlainText()!="":
                p3_y = float(self.valve_attribute_dlg.ui.teP3y.toPlainText())
            else:
                p3_y = 0.0

            if self.valve_attribute_dlg.ui.teP1dis.toPlainText()!="":
                p1_dist = float(self.valve_attribute_dlg.ui.teP1dis.toPlainText())
            else:
                p1_dist = 0.0

            if self.valve_attribute_dlg.ui.teP2dis.toPlainText()!="":
                p2_dist = float(self.valve_attribute_dlg.ui.teP2dis.toPlainText())
            else:
                p2_dist = 0.0

            if self.valve_attribute_dlg.ui.teP3dis.toPlainText()!="":
                p3_dist = float(self.valve_attribute_dlg.ui.teP3dis.toPlainText())
            else:
                p3_dist = 0.0
        
        elif item_text.split(' ')[0] == u'消防栓': 
            pidx = self.hydrant_attribute_dlg.ui.cbP1pos.currentIndex()
            print item_text.split(' ')[0]
            p1_type=''
            if pidx==1:
                p1_type='P1'
            elif pidx==2:
                p1_type='P2'
            elif pidx==3:
                p1_type='M1'
            elif pidx==4:
                p1_type='M2'
            elif pidx==5:
                p1_type='B1'
            elif pidx==6:
                p1_type='SL'
            elif pidx==7:
                p1_type='TL'
            elif pidx==8:
                p1_type='D1'
            elif pidx==9:
                p1_type='HC'
            elif pidx==10:
                p1_type='BD'
            elif pidx==11:
                p1_type='TR'
            elif pidx==12:
                p1_type='BM'
            elif pidx==13:
                p1_type='T1'
            elif pidx==14:
                p1_type='T2'
            elif pidx==15:
                p1_type='RI'
            elif pidx==16:
                p1_type='WT'
            elif pidx==17:
                p1_type='BW'
            elif pidx==18:
                p1_type='WA'
            elif pidx==19:
                p1_type='RS'
            elif pidx==20:
                p1_type='WN'
            elif pidx==21:
                p1_type='GP'
            elif pidx==22:
                p1_type='OT'

            pidx = self.hydrant_attribute_dlg.ui.cbP2pos.currentIndex()
            p2_type=''
            if pidx==1:
                p2_type='P1'
            elif pidx==2:
                p2_type='P2'
            elif pidx==3:
                p2_type='M1'
            elif pidx==4:
                p2_type='M2'
            elif pidx==5:
                p2_type='B1'
            elif pidx==6:
                p2_type='SL'
            elif pidx==7:
                p2_type='TL'
            elif pidx==8:
                p2_type='D1'
            elif pidx==9:
                p2_type='HC'
            elif pidx==10:
                p2_type='BD'
            elif pidx==11:
                p2_type='TR'
            elif pidx==12:
                p2_type='BM'
            elif pidx==13:
                p2_type='T1'
            elif pidx==14:
                p2_type='T2'
            elif pidx==15:
                p2_type='RI'
            elif pidx==16:
                p2_type='WT'
            elif pidx==17:
                p2_type='BW'
            elif pidx==18:
                p2_type='WA'
            elif pidx==19:
                p2_type='RS'
            elif pidx==20:
                p2_type='WN'
            elif pidx==21:
                p2_type='GP'
            elif pidx==22:
                p2_type='OT'

            pidx = self.hydrant_attribute_dlg.ui.cbP3pos.currentIndex()
            p3_type=''
            if pidx==1:
                p3_type='P1'
            elif pidx==2:
                p3_type='P2'
            elif pidx==3:
                p3_type='M1'
            elif pidx==4:
                p3_type='M2'
            elif pidx==5:
                p3_type='B1'
            elif pidx==6:
                p3_type='SL'
            elif pidx==7:
                p3_type='TL'
            elif pidx==8:
                p3_type='D1'
            elif pidx==9:
                p3_type='HC'
            elif pidx==10:
                p3_type='BD'
            elif pidx==11:
                p3_type='TR'
            elif pidx==12:
                p3_type='BM'
            elif pidx==13:
                p3_type='T1'
            elif pidx==14:
                p3_type='T2'
            elif pidx==15:
                p3_type='RI'
            elif pidx==16:
                p3_type='WT'
            elif pidx==17:
                p3_type='BW'
            elif pidx==18:
                p3_type='WA'
            elif pidx==19:
                p3_type='RS'
            elif pidx==20:
                p3_type='WN'
            elif pidx==21:
                p3_type='GP'
            elif pidx==22:
                p3_type='OT'

            #p1_type = u"'" + str(self.hydrant_attribute_dlg.ui.cbP1pos.currentIndex()) + u"'"
            #p2_type = u"'" + str(self.hydrant_attribute_dlg.ui.cbP2pos.currentIndex()) + u"'"
            #p3_type = u"'" + str(self.hydrant_attribute_dlg.ui.cbP3pos.currentIndex()) + u"'"
            p1_type = u"'" + p1_type + u"'"
            p2_type = u"'" + p2_type + u"'"
            p3_type = u"'" + p3_type + u"'"

            # 處理文字 lineEdit
            unific_id = u"'" + self.hydrant_attribute_dlg.ui.lineEdit_unific_id.text() + u"'"
            p1_desc = u"'" + self.hydrant_attribute_dlg.ui.teP1disc.toPlainText() + u"'"
            p2_desc = u"'" + self.hydrant_attribute_dlg.ui.teP2disc.toPlainText() + u"'"
            p3_desc = u"'" + self.hydrant_attribute_dlg.ui.teP3disc.toPlainText() + u"'"

            # 處理數字 lineEdit ，避免 數字 欄位，以空值(只有一個預設小數點)寫入 資料庫，型態不符所發生之錯誤
            if self.hydrant_attribute_dlg.ui.teP1x.toPlainText()!="":
                p1_x = float(self.hydrant_attribute_dlg.ui.teP1x.toPlainText())
            else:
                p1_x = 0.0

            if self.hydrant_attribute_dlg.ui.teP1y.toPlainText()!="":
                p1_y = float(self.hydrant_attribute_dlg.ui.teP1y.toPlainText())
            else:
                p1_y = 0.0

            if self.hydrant_attribute_dlg.ui.teP2x.toPlainText()!="":
                p2_x = float(self.hydrant_attribute_dlg.ui.teP2x.toPlainText())
            else:
                p2_x = 0.0

            if self.hydrant_attribute_dlg.ui.teP2y.toPlainText()!="":
                p2_y = float(self.hydrant_attribute_dlg.ui.teP2y.toPlainText())
            else:
                p2_y = 0.0
        
            if self.hydrant_attribute_dlg.ui.teP3x.toPlainText()!="":
                p3_x = float(self.hydrant_attribute_dlg.ui.teP3x.toPlainText())
            else:
                p3_x = 0.0

            if self.hydrant_attribute_dlg.ui.teP3y.toPlainText()!="":
                p3_y = float(self.hydrant_attribute_dlg.ui.teP3y.toPlainText())
            else:
                p3_y = 0.0

            if self.hydrant_attribute_dlg.ui.teP1dis.toPlainText()!="":
                p1_dist = float(self.hydrant_attribute_dlg.ui.teP1dis.toPlainText())
            else:
                p1_dist = 0.0

            if self.hydrant_attribute_dlg.ui.teP2dis.toPlainText()!="":
                p2_dist = float(self.hydrant_attribute_dlg.ui.teP2dis.toPlainText())
            else:
                p2_dist = 0.0

            if self.hydrant_attribute_dlg.ui.teP3dis.toPlainText()!="":
                p3_dist = float(self.hydrant_attribute_dlg.ui.teP3dis.toPlainText())
            else:
                p3_dist = 0.0

        elif item_text.split(' ')[0] == u'人手孔':  
                        
            pidx = self.manhole_attribute_dlg.ui.cbP1pos.currentIndex()
            p1_type=''
            if pidx==1:
                p1_type='P1'
            elif pidx==2:
                p1_type='P2'
            elif pidx==3:
                p1_type='M1'
            elif pidx==4:
                p1_type='M2'
            elif pidx==5:
                p1_type='B1'
            elif pidx==6:
                p1_type='SL'
            elif pidx==7:
                p1_type='TL'
            elif pidx==8:
                p1_type='D1'
            elif pidx==9:
                p1_type='HC'
            elif pidx==10:
                p1_type='BD'
            elif pidx==11:
                p1_type='TR'
            elif pidx==12:
                p1_type='BM'
            elif pidx==13:
                p1_type='T1'
            elif pidx==14:
                p1_type='T2'
            elif pidx==15:
                p1_type='RI'
            elif pidx==16:
                p1_type='WT'
            elif pidx==17:
                p1_type='BW'
            elif pidx==18:
                p1_type='WA'
            elif pidx==19:
                p1_type='RS'
            elif pidx==20:
                p1_type='WN'
            elif pidx==21:
                p1_type='GP'
            elif pidx==22:
                p1_type='OT'

            pidx = self.manhole_attribute_dlg.ui.cbP2pos.currentIndex()
            p2_type=''
            if pidx==1:
                p2_type='P1'
            elif pidx==2:
                p2_type='P2'
            elif pidx==3:
                p2_type='M1'
            elif pidx==4:
                p2_type='M2'
            elif pidx==5:
                p2_type='B1'
            elif pidx==6:
                p2_type='SL'
            elif pidx==7:
                p2_type='TL'
            elif pidx==8:
                p2_type='D1'
            elif pidx==9:
                p2_type='HC'
            elif pidx==10:
                p2_type='BD'
            elif pidx==11:
                p2_type='TR'
            elif pidx==12:
                p2_type='BM'
            elif pidx==13:
                p2_type='T1'
            elif pidx==14:
                p2_type='T2'
            elif pidx==15:
                p2_type='RI'
            elif pidx==16:
                p2_type='WT'
            elif pidx==17:
                p2_type='BW'
            elif pidx==18:
                p2_type='WA'
            elif pidx==19:
                p2_type='RS'
            elif pidx==20:
                p2_type='WN'
            elif pidx==21:
                p2_type='GP'
            elif pidx==22:
                p2_type='OT'

            pidx = self.manhole_attribute_dlg.ui.cbP3pos.currentIndex()
            p3_type=''
            if pidx==1:
                p3_type='P1'
            elif pidx==2:
                p3_type='P2'
            elif pidx==3:
                p3_type='M1'
            elif pidx==4:
                p3_type='M2'
            elif pidx==5:
                p3_type='B1'
            elif pidx==6:
                p3_type='SL'
            elif pidx==7:
                p3_type='TL'
            elif pidx==8:
                p3_type='D1'
            elif pidx==9:
                p3_type='HC'
            elif pidx==10:
                p3_type='BD'
            elif pidx==11:
                p3_type='TR'
            elif pidx==12:
                p3_type='BM'
            elif pidx==13:
                p3_type='T1'
            elif pidx==14:
                p3_type='T2'
            elif pidx==15:
                p3_type='RI'
            elif pidx==16:
                p3_type='WT'
            elif pidx==17:
                p3_type='BW'
            elif pidx==18:
                p3_type='WA'
            elif pidx==19:
                p3_type='RS'
            elif pidx==20:
                p3_type='WN'
            elif pidx==21:
                p3_type='GP'             
            elif pidx==22:
                p3_type='OT'             
            
            #p1_type = u"'" + str(self.manhole_attribute_dlg.ui.cbP1pos.currentIndex()) + u"'"
            #p2_type = u"'" + str(self.manhole_attribute_dlg.ui.cbP2pos.currentIndex()) + u"'"
            #p3_type = u"'" + str(self.manhole_attribute_dlg.ui.cbP3pos.currentIndex()) + u"'"
            p1_type = u"'" + p1_type + u"'"
            p2_type = u"'" + p2_type + u"'"
            p3_type = u"'" + p3_type + u"'"

            # 處理文字 lineEdit
            unific_id = u"'" + self.manhole_attribute_dlg.ui.lineEdit_unific_id.text() + u"'"
            p1_desc = u"'" + self.manhole_attribute_dlg.ui.teP1disc.toPlainText() + u"'"
            p2_desc = u"'" + self.manhole_attribute_dlg.ui.teP2disc.toPlainText() + u"'"
            p3_desc = u"'" + self.manhole_attribute_dlg.ui.teP3disc.toPlainText() + u"'"

            # 處理數字 lineEdit ，避免 數字 欄位，以空值(只有一個預設小數點)寫入 資料庫，型態不符所發生之錯誤
            if self.manhole_attribute_dlg.ui.teP1x.toPlainText()!="":
                p1_x = float(self.manhole_attribute_dlg.ui.teP1x.toPlainText())
            else:
                p1_x = 0.0

            if self.manhole_attribute_dlg.ui.teP1y.toPlainText()!="":
                p1_y = float(self.manhole_attribute_dlg.ui.teP1y.toPlainText())
            else:
                p1_y = 0.0

            if self.manhole_attribute_dlg.ui.teP2x.toPlainText()!="":
                p2_x = float(self.manhole_attribute_dlg.ui.teP2x.toPlainText())
            else:
                p2_x = 0.0

            if self.manhole_attribute_dlg.ui.teP2y.toPlainText()!="":
                p2_y = float(self.manhole_attribute_dlg.ui.teP2y.toPlainText())
            else:
                p2_y = 0.0
        
            if self.manhole_attribute_dlg.ui.teP3x.toPlainText()!="":
                p3_x = float(self.manhole_attribute_dlg.ui.teP3x.toPlainText())
            else:
                p3_x = 0.0

            if self.manhole_attribute_dlg.ui.teP3y.toPlainText()!="":
                p3_y = float(self.manhole_attribute_dlg.ui.teP3y.toPlainText())
            else:
                p3_y = 0.0

            if self.manhole_attribute_dlg.ui.teP1dis.toPlainText()!="":
                p1_dist = float(self.manhole_attribute_dlg.ui.teP1dis.toPlainText())
            else:
                p1_dist = 0.0

            if self.manhole_attribute_dlg.ui.teP2dis.toPlainText()!="":
                p2_dist = float(self.manhole_attribute_dlg.ui.teP2dis.toPlainText())
            else:
                p2_dist = 0.0

            if self.manhole_attribute_dlg.ui.teP3dis.toPlainText()!="":
                p3_dist = float(self.manhole_attribute_dlg.ui.teP3dis.toPlainText())
            else:
                p3_dist = 0.0


        db_conn = self.get_db_connection()
        query_string = "delete from surveytie WHERE unific_id='%s'" % str(self.unific_id_c)         
        print query_string
        query = db_conn.exec_(query_string)

        '''    
        print 'Query'

        #query_string = u"INSERT INTO surveytie (system_id,tp_no1,tp_type, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y, p1_desc, p2_desc, p3_desc, p1_dist, " \
        #query_string = u"INSERT INTO surveytie (system_id,unific_id,tp_type, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y, p1_desc, p2_desc, p3_desc, p1_dist, " \
        #  "p2_dist, p3_dist, p1_type, p2_type, p3_type) VALUES ({},{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) " \
        #  ''.format(system_id, unific_id,tp_type, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y, p1_desc, p2_desc, p3_desc, p1_dist, p2_dist, p3_dist, p1_type, p2_type, p3_type)
        
        print unific_id
        print p1_x
        print p1_y
        print p2_x
        print p2_y
        print p3_x
        print p3_y
        print p1_desc
        print p2_desc
        print p3_desc
        print p1_dist
        print p2_dist
        print p3_dist
        print p1_type
        print p2_type
        print p3_type
        '''
        
        query_string = u"INSERT INTO surveytie (unific_id, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y, p1_desc, p2_desc, p3_desc, p1_dist, " \
        "p2_dist, p3_dist, p1_type, p2_type, p3_type) VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) " \
        ''.format( unific_id, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y, p1_desc, p2_desc, p3_desc, p1_dist, p2_dist, p3_dist, p1_type, p2_type, p3_type)
        print query_string
        query = db_conn.exec_(query_string)
        # 檢查執行的 query 是否為有效!
        if query.isActive():
            query.clear()
            self.iface.mapCanvas().refresh()
            QMessageBox.information(self.iface.mainWindow(), u'修改三支距', u'資料修改完成!')
        else:
            QMessageBox.warning(self.iface.mainWindow(), u'修改三支距', u'資料庫寫入失敗!')
            
        # 關閉資料庫連線
        db_conn.close()
        del db_conn

    '''
    def draw_pin(self):
        global iButton
        p_list=[u'電力桿',u'電信桿',u'電力人孔',u'電信人孔',u'電信箱座',u'路燈',u'交通號誌',u'門柱',u'屋角',u'建物',u'三角點',u'水準點',u'變電箱座',u'變壓箱座',u'安全島',u'水池',u'板牆',u'圍牆',u'路邊',u'鐵絲網',u'路標','其他']

        db_conn = self.get_db_connection()
        query_string = "SELECT * FROM surveytie WHERE unific_id='%s'" %str(self.unific_id_c)
        print '5 '+self.unific_id_c
        query = db_conn.exec_(query_string)
        print 'draw_pin'
        print query_string
    
        layers = self.iface.legendInterface().layers()
        for Player in layers:
            layerType = Player.type()
            if layerType == QgsMapLayer.VectorLayer:       
                if Player.name() == "surveytie_p":       
                    break               

        for Llayer in layers:
            layerType = Llayer.type()
            if layerType == QgsMapLayer.VectorLayer:       
                if Llayer.name() == "surveytie_l":       
                    break     

        fields1 = Player.pendingFields()
        fields2 = Player.pendingFields()
        fields3 = Player.pendingFields()
        Lfields1 = Llayer.pendingFields()
        Lfields2 = Llayer.pendingFields()
        Lfields3 = Llayer.pendingFields()


        global iButton
        p_list=[u'電力桿',u'電信桿',u'電力人孔',u'電信人孔',u'電信箱座',u'路燈',u'交通號誌',u'門柱',u'屋角',u'建物',u'三角點',u'水準點',u'變電箱座',u'變壓箱座',u'安全島',u'水池',u'板牆',u'圍牆',u'路邊',u'鐵絲網',u'路標','其他']
        print self.px
        print self.py

        #展支距圖 
        db_conn = self.get_db_connection()
        query_string = u"delete FROM surveytie_p"
        query = db_conn.exec_(query_string)
        query_string = u"delete FROM surveytie_l"
        query = db_conn.exec_(query_string)
        #query_string = u"SELECT * FROM surveytie WHERE tp_no1='%s'" % str(g_uid)
        query_string = u"SELECT * FROM surveytie WHERE unific_id='%s'" % str(self.unific_id_c)
        query = db_conn.exec_(query_string)
            
        layers = self.iface.legendInterface().layers()
        for Player in layers:
            layerType = Player.type()
            if layerType == QgsMapLayer.VectorLayer:       
                if Player.name() == "surveytie_p":       
                    break               

        for Llayer in layers:
            layerType = Llayer.type()
            if layerType == QgsMapLayer.VectorLayer:       
                if Llayer.name() == "surveytie_l":       
                    break     

        fields1 = Player.pendingFields()
        fields2 = Player.pendingFields()
        fields3 = Player.pendingFields()
        Lfields1 = Llayer.pendingFields()
        Lfields2 = Llayer.pendingFields()
        Lfields3 = Llayer.pendingFields()

        i=1
        if query.isActive():
            while query.next():
                record = query.record() 
                f1 = QgsFeature(fields1)
                f2 = QgsFeature(fields2)
                f3 = QgsFeature(fields3)
                Lf1 = QgsFeature(Lfields1)
                Lf2 = QgsFeature(Lfields2)
                Lf3 = QgsFeature(Lfields3)


            if (float(record.field('p1_x').value())!=0) and (float(record.field('p1_y').value())!=0):
                for field in fields1.toList():
                    if field.name()=="gid":
                        f1[field.name()] = i
                    elif field.name()=="textstring":
                        str1=''
                        if record.field('p1_desc').value()!=NULL:
                            str1 =	u"%s" % record.field('p1_desc').value()
                        
                        str2=''
                        if record.field('p1_type').value()!=NULL:
                            #str2 =	u"%s" % record.field('p1_type').value()
                            if record.field('p1_type').value()=='P1':
                                str2 =	u"電力桿"
                            elif record.field('p1_type').value()=='P2':
                                str2 =	u"電信桿"
                            elif record.field('p1_type').value()=='M1':
                                str2 =	u"電力人孔"
                            elif record.field('p1_type').value()=='M2':
                                str2 =	u"電信人孔"
                            elif record.field('p1_type').value()=='B1':
                                str2 =	u"電信箱座"
                            elif record.field('p1_type').value()=='SL':
                                str2 =	u"路燈"
                            elif record.field('p1_type').value()=='TL':
                                str2 =	u"交通號誌"
                            elif record.field('p1_type').value()=='D1':
                                str2 =	u"門柱"
                            elif record.field('p1_type').value()=='HC':
                                str2 =	u"屋角"
                            elif record.field('p1_type').value()=='BD':
                                str2 =	u"建物"
                            elif record.field('p1_type').value()=='TR':
                                str2 =	u"三角點"
                            elif record.field('p1_type').value()=='BM':
                                str2 =	u"水準點"
                            elif record.field('p1_type').value()=='T1':
                                str2 =	u"變電箱座"
                            elif record.field('p1_type').value()=='T2':
                                str2 =	u"變壓箱座"
                            elif record.field('p1_type').value()=='RI':
                                str2 =	u"安全島"
                            elif record.field('p1_type').value()=='WT':
                                str2 =	u"水池"
                            elif record.field('p1_type').value()=='BW':
                                str2 =	u"板牆"
                            elif record.field('p1_type').value()=='WA':
                                str2 =	u"圍牆"
                            elif record.field('p1_type').value()=='RS':
                                str2 =	u"路邊"
                            elif record.field('p1_type').value()=='WN':
                                str2 =	u"鐵絲網"
                            elif record.field('p1_type').value()=='GP':
                                str2 =	u"路標"
                            elif record.field('p1_type').value()=='OT':
                                str2 =	u"其他"
                        
                        str3=''
                        if record.field('p1_dist').value()!=NULL:
                            str3 =	u"%s" % record.field('p1_dist').value()
                            f1[field.name()] = u"距【"+str1+str2+'】【'+str3+"】公尺"
                            #f1[field.name()] = u"距%s%s%s公尺" % (record.field('p1_desc').value(),p_list[int(record.field('p1_type').value())],str(record.field('p1_dist').value()))

                f1.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(record.field('p1_x').value()),float(record.field('p1_y').value()))))
                for field in Lfields1.toList():
                    if field.name()=="gid":
                        Lf1[field.name()] = i
                Lf1.setGeometry(QgsGeometry().fromPolyline([QgsPoint(px,py),QgsPoint(float(record.field('p1_x').value()),float(record.field('p1_y').value()))]))
                i=i+1

            if (float(record.field('p2_x').value())!=0) and (float(record.field('p2_y').value())!=0):
                for field in fields2.toList():
                    if field.name()=="gid":
                        f2[field.name()] = i
                    elif field.name()=="textstring":
                        str1=''
                        if record.field('p2_desc').value()!=NULL:
                            str1 =	u"%s" % record.field('p2_desc').value()
                        str2=''
                        if record.field('p2_type').value()!=NULL:
                        #str2 =	u"%s" % record.field('p2_type').value()
                            if record.field('p2_type').value()=='P1':
                                str2 =	u"電力桿"
                            elif record.field('p2_type').value()=='P2':
                                str2 =	u"電信桿"
                            elif record.field('p2_type').value()=='M1':
                                str2 =	u"電力人孔"
                            elif record.field('p2_type').value()=='M2':
                                str2 =	u"電信人孔"
                            elif record.field('p2_type').value()=='B1':
                                str2 =	u"電信箱座"
                            elif record.field('p2_type').value()=='SL':
                                str2 =	u"路燈"
                            elif record.field('p2_type').value()=='TL':
                                str2 =	u"交通號誌"
                            elif record.field('p2_type').value()=='D1':
                                str2 =	u"門柱"
                            elif record.field('p2_type').value()=='HC':
                                str2 =	u"屋角"
                            elif record.field('p2_type').value()=='BD':
                                str2 =	u"建物"
                            elif record.field('p2_type').value()=='TR':
                                str2 =	u"三角點"
                            elif record.field('p2_type').value()=='BM':
                                str2 =	u"水準點"
                            elif record.field('p2_type').value()=='T1':
                                str2 =	u"變電箱座"
                            elif record.field('p2_type').value()=='T2':
                                str2 =	u"變壓箱座"
                            elif record.field('p2_type').value()=='RI':
                                str2 =	u"安全島"
                            elif record.field('p2_type').value()=='WT':
                                str2 =	u"水池"
                            elif record.field('p2_type').value()=='BW':
                                str2 =	u"板牆"
                            elif record.field('p2_type').value()=='WA':
                                str2 =	u"圍牆"
                            elif record.field('p2_type').value()=='RS':
                                str2 =	u"路邊"
                            elif record.field('p2_type').value()=='WN':
                                str2 =	u"鐵絲網"
                            elif record.field('p2_type').value()=='GP':
                                str2 =	u"路標"                           
                            elif record.field('p2_type').value()=='OT':
                                str2 =	u"其他"                           
                        
                        str3=''
                        if record.field('p2_dist').value()!=NULL:
                            str3 =	u"%s" % record.field('p2_dist').value()
                        f2[field.name()] = u"距【"+str1+str2+'】【'+str3+"】公尺"
                        #f2[field.name()] = u"距%s%s%s公尺" % (record.field('p2_desc').value(),p_list[int(record.field('p2_type').value())],str(record.field('p2_dist').value()))
                f2.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(record.field('p2_x').value()),float(record.field('p2_y').value()))))
                for field in Lfields2.toList():
                    if field.name()=="gid":
                        Lf2[field.name()] = i
                Lf2.setGeometry(QgsGeometry().fromPolyline([QgsPoint(px,py),QgsPoint(float(record.field('p2_x').value()),float(record.field('p2_y').value()))]))
                i=i+1

            if (float(record.field('p3_x').value())!=0) and (float(record.field('p3_y').value())!=0):
                for field in fields3.toList():
                    if field.name()=="gid":
                        f3[field.name()] = i
                    elif field.name()=="textstring":
                        str1=''
                        if record.field('p3_desc').value()!=NULL:
                            str1 =	u"%s" % record.field('p3_desc').value()
                        str2=''
                        if record.field('p3_type').value()!=NULL:
                            #str2 =	u"%s" % record.field('p3_type').value()
                            
                                if record.field('p3_type').value()=='P1':
                                    str2 =	u"電力桿"
                                elif record.field('p3_type').value()=='P2':
                                    str2 =	u"電信桿"
                                elif record.field('p3_type').value()=='M1':
                                    str2 =	u"電力人孔"
                                elif record.field('p3_type').value()=='M2':
                                    str2 =	u"電信人孔"
                                elif record.field('p3_type').value()=='B1':
                                    str2 =	u"電信箱座"
                                elif record.field('p3_type').value()=='SL':
                                    str2 =	u"路燈"
                                elif record.field('p3_type').value()=='TL':
                                    str2 =	u"交通號誌"
                                elif record.field('p3_type').value()=='D1':
                                    str2 =	u"門柱"
                                elif record.field('p3_type').value()=='HC':
                                    str2 =	u"屋角"
                                elif record.field('p3_type').value()=='BD':
                                    str2 =	u"建物"
                                elif record.field('p3_type').value()=='TR':
                                    str2 =	u"三角點"
                                elif record.field('p3_type').value()=='BM':
                                    str2 =	u"水準點"
                                elif record.field('p3_type').value()=='T1':
                                    str2 =	u"變電箱座"
                                elif record.field('p3_type').value()=='T2':
                                    str2 =	u"變壓箱座"
                                elif record.field('p3_type').value()=='RI':
                                    str2 =	u"安全島"
                                elif record.field('p3_type').value()=='WT':
                                    str2 =	u"水池"
                                elif record.field('p3_type').value()=='BW':
                                    str2 =	u"板牆"
                                elif record.field('p3_type').value()=='WA':
                                    str2 =	u"圍牆"
                                elif record.field('p3_type').value()=='RS':
                                    str2 =	u"路邊"
                                elif record.field('p3_type').value()=='WN':
                                    str2 =	u"鐵絲網"
                                elif record.field('p3_type').value()=='GP':
                                    str2 =	u"路標"                      	       
                                elif record.field('p3_type').value()=='OT':
                                    str2 =	u"其他"                      	       
                            
                            
                        str3=''
                        if record.field('p3_dist').value()!=NULL:
                            str3 =	u"%s" % record.field('p3_dist').value()
                        f3[field.name()] = u"距【"+str1+str2+'】【'+str3+"】公尺"
                        #f3[field.name()] = u"距%s%s%s公尺" % (record.field('p3_desc').value(),p_list[int(record.field('p3_type').value())],str(record.field('p3_dist').value()))
                f3.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(record.field('p3_x').value()),float(record.field('p3_y').value()))))
                for field in Lfields3.toList():
                    if field.name()=="gid":
                        Lf3[field.name()] = i
                Lf3.setGeometry(QgsGeometry().fromPolyline([QgsPoint(px,py),QgsPoint(float(record.field('p3_x').value()),float(record.field('p3_y').value()))]))
                i=i+1
            

        Player.startEditing()
        if i==2:
            Player.addFeature(f1, True)
        if i==3:
            Player.addFeature(f1, True)
            Player.addFeature(f2, True)
        if i==4:
            Player.addFeature(f1, True)
            Player.addFeature(f2, True)
            Player.addFeature(f3, True)
        Player.commitChanges()   

        Llayer.startEditing()
        if i==2:
            Llayer.addFeature(Lf1, True)
        if i==3:
            Llayer.addFeature(Lf1, True)
            Llayer.addFeature(Lf2, True)
        if i==4:
            Llayer.addFeature(Lf1, True)
            Llayer.addFeature(Lf2, True)
            Llayer.addFeature(Lf3, True)
        Llayer.commitChanges()   
        self.canvas.refresh()                	           
    '''
    def deactivate(self):
        self.action_attribute_edit.setChecked(False)
        QObject.disconnect(self.edit_features_tool, SIGNAL('featureIdentified'), self.confirm_area)

        self.acton_attribute_edit.setChecked(False)
        QObject.disconnect(self.drawline, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.confirm_geom)


    def get_db_connection(self):

        layer = self.canvas.layer(0)

        provider = layer.dataProvider()

        if provider.name() == 'postgres':
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