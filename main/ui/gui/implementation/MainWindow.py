from PyQt5.QtWidgets import QFileDialog

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.ui.common.JSONGlobalModelParser import JSONGlobalModelParser
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
        # Path of the input validate schema
        # Warning: In python paths are relative to the entry point script path
        input_schema_path = './main/ui/cli/input_schema/input-schema.json'

        # Read schema
        error, message, schema_object = JSONGlobalModelParser.read_input(input_schema_path)

        if error:
            self.label_status.setText(message)

        # Read input
        error, message, input_object = JSONGlobalModelParser.read_input(path)

        if error:
            self.label_status.setText(message)

        # Validate schema
        error, message = JSONGlobalModelParser.validate_input(input_object, schema_object)

        if error:
            self.label_status.setText(message)

        # Fill fields
        global_specification, _, _ = JSONGlobalModelParser.obtain_global_model(input_object)
        global_specification: GlobalSpecification = global_specification
        if global_specification.simulation_specification.simulate_thermal:
            self.checkBox_simulation_thermal.clicked(True)
        else:
            self.checkBox_simulation_thermal.clicked(False)
        # TODO: Put fields in inputs

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
