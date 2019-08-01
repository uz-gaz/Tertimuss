# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design/gui_add_origin_design.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogAddOrigin(object):
    def setupUi(self, DialogAddOrigin):
        DialogAddOrigin.setObjectName("DialogAddOrigin")
        DialogAddOrigin.resize(400, 136)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogAddOrigin)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(DialogAddOrigin)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.doubleSpinBox_x = QtWidgets.QDoubleSpinBox(DialogAddOrigin)
        self.doubleSpinBox_x.setDecimals(5)
        self.doubleSpinBox_x.setMaximum(99999.99999)
        self.doubleSpinBox_x.setObjectName("doubleSpinBox_x")
        self.horizontalLayout.addWidget(self.doubleSpinBox_x)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(DialogAddOrigin)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.doubleSpinBox_y = QtWidgets.QDoubleSpinBox(DialogAddOrigin)
        self.doubleSpinBox_y.setDecimals(5)
        self.doubleSpinBox_y.setMaximum(99999.99999)
        self.doubleSpinBox_y.setObjectName("doubleSpinBox_y")
        self.horizontalLayout_2.addWidget(self.doubleSpinBox_y)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.pushButton_add = QtWidgets.QPushButton(DialogAddOrigin)
        self.pushButton_add.setObjectName("pushButton_add")
        self.horizontalLayout_4.addWidget(self.pushButton_add)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.label.setBuddy(self.doubleSpinBox_x)
        self.label_2.setBuddy(self.doubleSpinBox_y)

        self.retranslateUi(DialogAddOrigin)
        self.pushButton_add.clicked.connect(DialogAddOrigin.accept)
        self.pushButton_add.clicked.connect(DialogAddOrigin.add_clicked)
        QtCore.QMetaObject.connectSlotsByName(DialogAddOrigin)

    def retranslateUi(self, DialogAddOrigin):
        _translate = QtCore.QCoreApplication.translate
        DialogAddOrigin.setWindowTitle(_translate("DialogAddOrigin", "Dialog"))
        self.label.setText(_translate("DialogAddOrigin", "x (mm)"))
        self.label_2.setText(_translate("DialogAddOrigin", "y (mm)"))
        self.pushButton_add.setText(_translate("DialogAddOrigin", "Add"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DialogAddOrigin = QtWidgets.QDialog()
    ui = Ui_DialogAddOrigin()
    ui.setupUi(DialogAddOrigin)
    DialogAddOrigin.show()
    sys.exit(app.exec_())

