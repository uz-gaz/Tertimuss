from main.ui.common.OutputSelector import OutputSelector
from main.ui.gui.ui_specification.implementation.gui_output_desing import *


class AddOutputDialog(QtWidgets.QDialog, Ui_DialogAddOutput):
    """
    Add output window
    """

    def __init__(self, is_thermal_enabled: bool, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.__return_value = None

        outputs_names = OutputSelector.get_output_names_thermal() if is_thermal_enabled \
            else OutputSelector.get_output_names_no_thermal()

        for i in range(len(outputs_names)):
            self.comboBox_output.addItem("")
            self.comboBox_output.setItemText(i, outputs_names[i])

    def add_clicked(self):
        self.__return_value = [self.comboBox_output.currentText()]

    def get_return_value(self):
        return self.__return_value
