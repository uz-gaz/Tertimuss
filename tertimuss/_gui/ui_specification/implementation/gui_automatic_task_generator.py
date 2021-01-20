# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design/gui_automatic_task_generator.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(479, 248)
        Dialog.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.spinBox_period_start = QtWidgets.QSpinBox(Dialog)
        self.spinBox_period_start.setObjectName("spinBox_period_start")
        self.horizontalLayout.addWidget(self.spinBox_period_start)
        self.spinBox_period_end = QtWidgets.QSpinBox(Dialog)
        self.spinBox_period_end.setObjectName("spinBox_period_end")
        self.horizontalLayout.addWidget(self.spinBox_period_end)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.spinBox_number_of_tasks = QtWidgets.QSpinBox(Dialog)
        self.spinBox_number_of_tasks.setObjectName("spinBox_number_of_tasks")
        self.horizontalLayout_2.addWidget(self.spinBox_number_of_tasks)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.doubleSpinBox_utilization = QtWidgets.QDoubleSpinBox(Dialog)
        self.doubleSpinBox_utilization.setMaximum(99.0)
        self.doubleSpinBox_utilization.setObjectName("doubleSpinBox_utilization")
        self.horizontalLayout_3.addWidget(self.doubleSpinBox_utilization)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.comboBox_algorithm_name = QtWidgets.QComboBox(Dialog)
        self.comboBox_algorithm_name.setObjectName("comboBox_algorithm_name")
        self.horizontalLayout_4.addWidget(self.comboBox_algorithm_name)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem4)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_5.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.label.setBuddy(self.spinBox_period_start)
        self.label_2.setBuddy(self.spinBox_number_of_tasks)
        self.label_3.setBuddy(self.doubleSpinBox_utilization)
        self.label_4.setBuddy(self.comboBox_algorithm_name)

        self.retranslateUi(Dialog)
        self.pushButton.clicked.connect(Dialog.add_clicked)
        self.pushButton.clicked.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Automatic task generator"))
        self.label.setText(_translate("Dialog", "Periods intervals"))
        self.label_2.setText(_translate("Dialog", "Number of tasks"))
        self.label_3.setText(_translate("Dialog", "Utilization"))
        self.label_4.setText(_translate("Dialog", "Algorithm name"))
        self.pushButton.setText(_translate("Dialog", "Add"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

