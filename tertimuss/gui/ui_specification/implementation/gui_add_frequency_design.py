# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design/gui_add_frequency_design.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogAddFrequency(object):
    def setupUi(self, DialogAddFrequency):
        DialogAddFrequency.setObjectName("DialogAddFrequency")
        DialogAddFrequency.setWindowModality(QtCore.Qt.NonModal)
        DialogAddFrequency.setEnabled(True)
        DialogAddFrequency.resize(605, 128)
        DialogAddFrequency.setSizeGripEnabled(False)
        DialogAddFrequency.setModal(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogAddFrequency)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(DialogAddFrequency)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.spinBox_frequency = QtWidgets.QSpinBox(DialogAddFrequency)
        self.spinBox_frequency.setMaximum(99999)
        self.spinBox_frequency.setSingleStep(100)
        self.spinBox_frequency.setObjectName("spinBox_frequency")
        self.horizontalLayout.addWidget(self.spinBox_frequency)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.pushButton_add = QtWidgets.QPushButton(DialogAddFrequency)
        self.pushButton_add.setObjectName("pushButton_add")
        self.horizontalLayout_4.addWidget(self.pushButton_add)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.label.setBuddy(self.spinBox_frequency)

        self.retranslateUi(DialogAddFrequency)
        self.pushButton_add.clicked.connect(DialogAddFrequency.accept)
        self.pushButton_add.clicked.connect(DialogAddFrequency.add_clicked)
        QtCore.QMetaObject.connectSlotsByName(DialogAddFrequency)

    def retranslateUi(self, DialogAddFrequency):
        _translate = QtCore.QCoreApplication.translate
        DialogAddFrequency.setWindowTitle(_translate("DialogAddFrequency", "Dialog"))
        self.label.setText(_translate("DialogAddFrequency", "Frequency (Hz)"))
        self.pushButton_add.setText(_translate("DialogAddFrequency", "Add"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DialogAddFrequency = QtWidgets.QDialog()
    ui = Ui_DialogAddFrequency()
    ui.setupUi(DialogAddFrequency)
    DialogAddFrequency.show()
    sys.exit(app.exec_())

