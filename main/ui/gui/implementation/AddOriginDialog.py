from main.ui.gui.ui_specification.implementation.gui_add_origin_design import *


class AddOriginDialog(QtWidgets.QDialog, Ui_DialogAddOrigin):
    """
    Add origin window
    """

    def __init__(self, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.__return_value = None

    def add_clicked(self):
        self.__return_value = [self.doubleSpinBox_x, self.doubleSpinBox_y]

    def get_return_value(self):
        return self.__return_value
