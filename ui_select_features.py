# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_select_features.ui'
#
# Created: Mon Dec 03 11:09:38 2018
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SelectFeatures(object):
    def setupUi(self, SelectFeatures):
        SelectFeatures.setObjectName(_fromUtf8("SelectFeatures"))
        SelectFeatures.resize(295, 256)
        self.comboBoxLayer = QtGui.QComboBox(SelectFeatures)
        self.comboBoxLayer.setGeometry(QtCore.QRect(70, 90, 160, 32))
        self.comboBoxLayer.setObjectName(_fromUtf8("comboBoxLayer"))
        self.pushButtonOK = QtGui.QPushButton(SelectFeatures)
        self.pushButtonOK.setGeometry(QtCore.QRect(70, 130, 80, 32))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButtonOK.setFont(font)
        self.pushButtonOK.setObjectName(_fromUtf8("pushButtonOK"))
        self.pushButtonCancel = QtGui.QPushButton(SelectFeatures)
        self.pushButtonCancel.setGeometry(QtCore.QRect(150, 130, 80, 32))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButtonCancel.setFont(font)
        self.pushButtonCancel.setObjectName(_fromUtf8("pushButtonCancel"))
        self.labelLayer = QtGui.QLabel(SelectFeatures)
        self.labelLayer.setGeometry(QtCore.QRect(70, 50, 160, 32))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelLayer.setFont(font)
        self.labelLayer.setAlignment(QtCore.Qt.AlignCenter)
        self.labelLayer.setObjectName(_fromUtf8("labelLayer"))
        self.overlap = QtGui.QLineEdit(SelectFeatures)
        self.overlap.setGeometry(QtCore.QRect(70, 190, 161, 31))
        self.overlap.setObjectName(_fromUtf8("overlap"))

        self.retranslateUi(SelectFeatures)
        QtCore.QMetaObject.connectSlotsByName(SelectFeatures)

    def retranslateUi(self, SelectFeatures):
        SelectFeatures.setWindowTitle(_translate("SelectFeatures", "Form", None))
        self.pushButtonOK.setText(_translate("SelectFeatures", "確認", None))
        self.pushButtonCancel.setText(_translate("SelectFeatures", "取消", None))
        self.labelLayer.setText(_translate("SelectFeatures", "請選取設施類別", None))

