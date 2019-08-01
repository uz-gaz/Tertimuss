from main.ui.gui.ui_specification.implementation.gui_add_frequency_design import *


class AddFrequencyDialog(QtWidgets.QDialog, Ui_DialogAddFrequency):
    def __init__(self, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.__return_value = None

    def add_clicked(self):
        self.__return_value = [self.spinBox_frequency.value()]

    def get_return_value(self):
        return self.__return_value
