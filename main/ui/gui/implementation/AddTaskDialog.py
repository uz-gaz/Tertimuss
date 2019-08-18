from main.ui.gui.ui_specification.implementation.gui_add_task_design import *


class AddTaskDialog(QtWidgets.QDialog, Ui_DialogAddTask):
    """
    Add tasks window
    """

    def __init__(self, is_thermal_enabled: bool, is_energy_enabled: bool, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.is_thermal_enabled = is_thermal_enabled
        self.is_energy_enabled = is_energy_enabled
        self.__return_value = None

    def add_clicked(self):
        self.__return_value = [
            self.comboBox_type.currentText(),
            self.doubleSpinBox_WCET.value(),
            self.doubleSpinBox_arrive.value() if self.comboBox_type.currentText() != "Periodic" else None,
            self.doubleSpinBox_deadline.value(),
            self.doubleSpinBox_energy.value() if self.is_thermal_enabled or self.is_energy_enabled else None
        ]

    def get_return_value(self):
        return self.__return_value

    def change_type(self, new_type: str):
        self.doubleSpinBox_arrive.setEnabled(new_type != "Periodic")
        self.label_arrive.setEnabled(new_type != "Periodic")
