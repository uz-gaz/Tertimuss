# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design\gui_output_desing.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogAddOutput(object):
    def setupUi(self, DialogAddOutput):
        DialogAddOutput.setObjectName("DialogAddOutput")
        DialogAddOutput.resize(359, 90)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogAddOutput)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_35 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_35.setObjectName("horizontalLayout_35")
        self.label_27 = QtWidgets.QLabel(DialogAddOutput)
        self.label_27.setObjectName("label_27")
        self.horizontalLayout_35.addWidget(self.label_27)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_35.addItem(spacerItem)
        self.comboBox_output = QtWidgets.QComboBox(DialogAddOutput)
        self.comboBox_output.setObjectName("comboBox_output")
        self.horizontalLayout_35.addWidget(self.comboBox_output)
        self.verticalLayout.addLayout(self.horizontalLayout_35)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pushButton_add = QtWidgets.QPushButton(DialogAddOutput)
        self.pushButton_add.setObjectName("pushButton_add")
        self.horizontalLayout.addWidget(self.pushButton_add)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_27.setBuddy(self.comboBox_output)

        self.retranslateUi(DialogAddOutput)
        QtCore.QMetaObject.connectSlotsByName(DialogAddOutput)

    def retranslateUi(self, DialogAddOutput):
        _translate = QtCore.QCoreApplication.translate
        DialogAddOutput.setWindowTitle(_translate("DialogAddOutput", "Dialog"))
        self.label_27.setText(_translate("DialogAddOutput", "Output"))
        self.pushButton_add.setText(_translate("DialogAddOutput", "Add"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DialogAddOutput = QtWidgets.QDialog()
    ui = Ui_DialogAddOutput()
    ui.setupUi(DialogAddOutput)
    DialogAddOutput.show()
    sys.exit(app.exec_())

