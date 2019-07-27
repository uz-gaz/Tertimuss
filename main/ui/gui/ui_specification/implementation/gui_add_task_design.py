# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design\gui_add_task_design.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogAddTask(object):
    def setupUi(self, DialogAddTask):
        DialogAddTask.setObjectName("DialogAddTask")
        DialogAddTask.resize(528, 164)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogAddTask)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(DialogAddTask)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.doubleSpinBox_WCET = QtWidgets.QDoubleSpinBox(DialogAddTask)
        self.doubleSpinBox_WCET.setObjectName("doubleSpinBox_WCET")
        self.horizontalLayout.addWidget(self.doubleSpinBox_WCET)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(DialogAddTask)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.doubleSpinBox_deadline = QtWidgets.QDoubleSpinBox(DialogAddTask)
        self.doubleSpinBox_deadline.setObjectName("doubleSpinBox_deadline")
        self.horizontalLayout_2.addWidget(self.doubleSpinBox_deadline)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(DialogAddTask)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.doubleSpinBox_energy = QtWidgets.QDoubleSpinBox(DialogAddTask)
        self.doubleSpinBox_energy.setObjectName("doubleSpinBox_energy")
        self.horizontalLayout_3.addWidget(self.doubleSpinBox_energy)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.pushButton_add = QtWidgets.QPushButton(DialogAddTask)
        self.pushButton_add.setObjectName("pushButton_add")
        self.horizontalLayout_4.addWidget(self.pushButton_add)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.label.setBuddy(self.doubleSpinBox_WCET)
        self.label_2.setBuddy(self.doubleSpinBox_deadline)
        self.label_3.setBuddy(self.doubleSpinBox_energy)

        self.retranslateUi(DialogAddTask)
        self.pushButton_add.clicked.connect(DialogAddTask.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogAddTask)

    def retranslateUi(self, DialogAddTask):
        _translate = QtCore.QCoreApplication.translate
        DialogAddTask.setWindowTitle(_translate("DialogAddTask", "Dialog"))
        self.label.setText(_translate("DialogAddTask", "Worst case execution time"))
        self.label_2.setText(_translate("DialogAddTask", "Task period, equal to deadline"))
        self.label_3.setText(_translate("DialogAddTask", "Energy consumption"))
        self.pushButton_add.setText(_translate("DialogAddTask", "Add"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DialogAddTask = QtWidgets.QDialog()
    ui = Ui_DialogAddTask()
    ui.setupUi(DialogAddTask)
    DialogAddTask.show()
    sys.exit(app.exec_())

