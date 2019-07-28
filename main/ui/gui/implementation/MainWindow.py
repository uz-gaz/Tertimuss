from PyQt5.QtWidgets import QFileDialog

from main.ui.common.SchedulerSelector import SchedulerSelector
from main.ui.common.TCPNThermalModelSelector import TCPNThermalModelSelector
from main.ui.gui.ui_specification.implementation.gui_main_desing import *

import sys


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # Control thermal enabled/disabled
        self.checkBox_simulation_thermal.toggled.connect(
            lambda x: self.doubleSpinBox_simulation_mesh_step.setEnabled(x))
        self.checkBox_simulation_thermal.toggled.connect(lambda x: self.comboBox_simulation_energy_model.setEnabled(x))
        self.checkBox_simulation_thermal.toggled.connect(lambda x: self.tab_environment.setEnabled(x))
        self.checkBox_simulation_thermal.toggled.connect(lambda x: self.tab_board.setEnabled(x))
        self.checkBox_simulation_thermal.toggled.connect(lambda x: self.tab_cpu_cores_physical.setEnabled(x))
        self.checkBox_simulation_thermal.toggled.connect(lambda x: self.tab_cpu_cores_origins.setEnabled(x))
        self.checkBox_simulation_thermal.toggled.connect(lambda x: self.tab_cpu_cores_energy.setEnabled(x))
        self.checkBox_simulation_thermal.toggled.connect(
            lambda x: self.checkBox_cpu_cores_automatic_origins.setEnabled(x))
        # TODO: Disable in add task the energy form
        # TODO: Disable some outputs

        # Control automatic origins enabled/disabled
        self.checkBox_cpu_cores_automatic_origins.toggled.connect(
            lambda x: self.tab_cpu_cores_origins.setEnabled(not x))

        # Energy generation model
        _translate = QtCore.QCoreApplication.translate
        tcpn_model_names = TCPNThermalModelSelector.get_tcpn_model_names()

        for i in range(len(tcpn_model_names)):
            self.comboBox_simulation_energy_model.addItem("")
            self.comboBox_simulation_energy_model.setItemText(i, _translate("MainWindow", tcpn_model_names[i]))

        # Available schedulers
        scheduler_names = SchedulerSelector.get_scheduler_names()

        for i in range(len(scheduler_names)):
            self.comboBox_scheduler_select.addItem("")
            self.comboBox_scheduler_select.setItemText(i, _translate("MainWindow", scheduler_names[i]))

        # TODO: Open browser to search JSON

        # TODO: Open browser to search output

    def simulate_thermal_state_changed(self, state: bool):
        print("simulate_thermal_state_changed")

    def load_json(self):
        print("load_json")

    def start_simulation(self):
        print("start_simulation")

    def add_task(self):
        print("add_task")

    def generate_automatic_tasks(self):
        print("generate_automatic_tasks")

    def add_origin(self):
        print("add_origin")

    def add_available_frequency(self):
        print("add_available_frequency")

    def add_selected_frequency(self):
        print("add_selected_frequency")

    def generate_automatic_origins_changed(self, state: bool):
        print("generate_automatic_origins_changed")

    def change_output_path(self):
        print("change_output_path")

    def add_output(self):
        print("add_output")

    def __load_json_clicked(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*)",
                                                   options=options)
        if file_name:
            print(file_name)

    def get_data(self):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
