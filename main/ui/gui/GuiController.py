from ui_specification.gui_structure import *

import sys


class MainWindow(QtWidgets.QMainWindow, Ui_Dialog):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        r = self.doubleSpinBox.value()  # Obtiene float
        # self.label.setText("Haz clic en el botón")
        # self.pushButton.setText("Presióname")
        # self.pushButton.clicked.connect(self.actualizar)

    def actualizar(self):
        self.label.setText("¡Acabas de hacer clic en el botón!")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = MainWindow()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
