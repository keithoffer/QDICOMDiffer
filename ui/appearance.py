# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'appearance.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogAppearance(object):
    def setupUi(self, DialogAppearance):
        DialogAppearance.setObjectName("DialogAppearance")
        DialogAppearance.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogAppearance)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelNormalRow = QtWidgets.QLabel(DialogAppearance)
        self.labelNormalRow.setObjectName("labelNormalRow")
        self.verticalLayout.addWidget(self.labelNormalRow)
        self.labelDirectMatchedRow = QtWidgets.QLabel(DialogAppearance)
        self.labelDirectMatchedRow.setObjectName("labelDirectMatchedRow")
        self.verticalLayout.addWidget(self.labelDirectMatchedRow)
        self.labelIndirectMatchedRow = QtWidgets.QLabel(DialogAppearance)
        self.labelIndirectMatchedRow.setObjectName("labelIndirectMatchedRow")
        self.verticalLayout.addWidget(self.labelIndirectMatchedRow)
        self.pushButtonChangeFont = QtWidgets.QPushButton(DialogAppearance)
        self.pushButtonChangeFont.setObjectName("pushButtonChangeFont")
        self.verticalLayout.addWidget(self.pushButtonChangeFont)
        self.pushButtonChangeDirectColour = QtWidgets.QPushButton(DialogAppearance)
        self.pushButtonChangeDirectColour.setObjectName("pushButtonChangeDirectColour")
        self.verticalLayout.addWidget(self.pushButtonChangeDirectColour)
        self.pushButtonChangeIndirectColour = QtWidgets.QPushButton(DialogAppearance)
        self.pushButtonChangeIndirectColour.setObjectName("pushButtonChangeIndirectColour")
        self.verticalLayout.addWidget(self.pushButtonChangeIndirectColour)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogAppearance)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DialogAppearance)
        self.buttonBox.accepted.connect(DialogAppearance.accept)
        self.buttonBox.rejected.connect(DialogAppearance.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogAppearance)

    def retranslateUi(self, DialogAppearance):
        _translate = QtCore.QCoreApplication.translate
        DialogAppearance.setWindowTitle(_translate("DialogAppearance", "Appearance"))
        self.labelNormalRow.setText(_translate("DialogAppearance", "Normal row"))
        self.labelDirectMatchedRow.setText(_translate("DialogAppearance", "Directly matched row"))
        self.labelIndirectMatchedRow.setText(_translate("DialogAppearance", "Indirectly matched row"))
        self.pushButtonChangeFont.setText(_translate("DialogAppearance", "Change font"))
        self.pushButtonChangeDirectColour.setText(_translate("DialogAppearance", "Change direct match background colour"))
        self.pushButtonChangeIndirectColour.setText(_translate("DialogAppearance", "Change indirect match background colour"))

