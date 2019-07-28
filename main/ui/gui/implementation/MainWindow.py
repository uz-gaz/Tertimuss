from PyQt5.QtWidgets import QFileDialog

from main.ui.common.SchedulerSelector import SchedulerSelector
from main.ui.common.TCPNThermalModelSelector import TCPNThermalModelSelector
from main.ui.gui.ui_specification.implementation.gui_main_desing import *

import sys


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

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

    def simulate_thermal_state_changed(self, state: bool):
        # Control thermal enabled/disabled
        self.doubleSpinBox_simulation_mesh_step.setEnabled(state)
        self.comboBox_simulation_energy_model.setEnabled(state)
        self.tab_environment.setEnabled(state)
        self.tab_board.setEnabled(state)
        self.tab_cpu_cores_physical.setEnabled(state)
        self.tab_cpu_cores_origins.setEnabled(state)
        self.tab_cpu_cores_energy.setEnabled(state)
        self.checkBox_cpu_cores_automatic_origins.setEnabled(state)
        # TODO: Disable in add task the energy form
        # TODO: Disable some outputs

    def load_json(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load specification", "", "JSON (*.json)",
                                                   options=options)
        if file_name:
            self.__load_json_input(file_name)

    def __load_json_input(self, path: str):
        # TODO: Load json input
        # TODO: Validate fields
        # TODO: Put fields in inputs
        pass

    def start_simulation(self):
        # TODO: Save as JSON
        # TODO: Use the JSON in the same way as CLI
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
        # Control automatic origins enabled/disabled
        self.tab_cpu_cores_origins.setEnabled(not state)

    def change_output_path(self):
        # TODO: Open browser to search output
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
