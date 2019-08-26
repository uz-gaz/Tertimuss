from PyQt5 import QtWidgets

from main.ui.gui.implementation.MainWindow import MainWindow


class GuiController(object):
    @staticmethod
    def gui_main() -> int:
        """
        Launch main
        :return: GUI return code
        """
        gui_app_args = []
        app = QtWidgets.QApplication(gui_app_args)
        ui = MainWindow()
        ui.show()
        return app.exec_()
