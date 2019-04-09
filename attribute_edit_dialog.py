# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AttributeEditDialog
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

import os

from PyQt4 import *
from qgis.core import *
from qgis.utils import *

from ui_pick_features import Ui_PickFeatures
from ui_select_features import Ui_SelectFeatures
from ui_valve_attribute import Ui_ValveAttribute
from ui_manhole_attribute import Ui_ManholeAttribute
from ui_hydrant_attribute import Ui_HydrantAttribute

class PickFeaturesDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self, iface.mainWindow())
        self.ui = Ui_PickFeatures()
        self.ui.setupUi(self)

class SelectFeaturesDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self, iface.mainWindow())
        self.ui = Ui_SelectFeatures()
        self.ui.setupUi(self)

class ValveAttributeDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self, iface.mainWindow())
        self.ui = Ui_ValveAttribute()
        self.ui.setupUi(self)

class ManholeAttributeDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self, iface.mainWindow())
        self.ui = Ui_ManholeAttribute()
        self.ui.setupUi(self)

class HydrantAttributeDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self, iface.mainWindow())
        self.ui = Ui_HydrantAttribute()
        self.ui.setupUi(self)