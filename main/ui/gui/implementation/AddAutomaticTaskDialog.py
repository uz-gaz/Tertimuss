from main.ui.common.TaskGeneratorSelector import TaskGeneratorSelector
from main.ui.gui.ui_specification.implementation.gui_automatic_task_generator import *


class AddAutomaticTaskDialog(QtWidgets.QDialog, Ui_Dialog):
    """
    Generate automatic tasks window
    """

    def __init__(self, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)

        task_generators_names = TaskGeneratorSelector.get_task_generators_names()

        for i in range(len(task_generators_names)):
            self.comboBox_algorithm_name.addItem("")
            self.comboBox_algorithm_name.setItemText(i, task_generators_names[i])

        self.__return_value = None

    def add_clicked(self):
        self.__return_value = [
            self.spinBox_period_start.value(),
            self.spinBox_period_end.value(),
            self.spinBox_number_of_tasks.value(),
            self.doubleSpinBox_utilization.value(),
            self.comboBox_algorithm_name.currentText()
        ]

    def get_return_value(self):
        return self.__return_value
