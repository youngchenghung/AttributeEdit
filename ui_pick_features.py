# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_pick_features.ui'
#
# Created: Tue Dec 18 13:55:50 2018
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

class Ui_PickFeatures(object):
    def setupUi(self, PickFeatures):
        PickFeatures.setObjectName(_fromUtf8("PickFeatures"))
        PickFeatures.resize(288, 304)
        self.label_pick = QtGui.QLabel(PickFeatures)
        self.label_pick.setGeometry(QtCore.QRect(16, 16, 256, 32))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_pick.setFont(font)
        self.label_pick.setAlignment(QtCore.Qt.AlignCenter)
        self.label_pick.setObjectName(_fromUtf8("label_pick"))
        self.listWidget_pick = QtGui.QListWidget(PickFeatures)
        self.listWidget_pick.setGeometry(QtCore.QRect(16, 56, 256, 192))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.listWidget_pick.setFont(font)
        self.listWidget_pick.setObjectName(_fromUtf8("listWidget_pick"))
        self.pushButton_Cancel = QtGui.QPushButton(PickFeatures)
        self.pushButton_Cancel.setGeometry(QtCore.QRect(16, 256, 256, 32))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_Cancel.setFont(font)
        self.pushButton_Cancel.setObjectName(_fromUtf8("pushButton_Cancel"))

        self.retranslateUi(PickFeatures)
        QtCore.QMetaObject.connectSlotsByName(PickFeatures)

    def retranslateUi(self, PickFeatures):
        PickFeatures.setWindowTitle(_translate("PickFeatures", "Dialog", None))
        self.label_pick.setText(_translate("PickFeatures", "請點選物件範圍資料", None))
        self.pushButton_Cancel.setText(_translate("PickFeatures", "關閉", None))

