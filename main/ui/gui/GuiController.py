import sys

from PyQt5 import QtWidgets

from main.ui.gui.implementation.MainWindow import MainWindow


class GuiController(object):
    @staticmethod
    def gui_main(args):
        app = QtWidgets.QApplication(sys.argv)
        ui = MainWindow()
        ui.show()
        sys.exit(app.exec_())
