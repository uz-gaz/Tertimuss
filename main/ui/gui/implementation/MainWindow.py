from PyQt5.QtWidgets import QFileDialog

from main.ui.common.JSONGlobalModelParser import JSONGlobalModelParser
from main.ui.common.SchedulerSelector import SchedulerSelector
from main.ui.common.TCPNThermalModelSelector import TCPNThermalModelSelector
from main.ui.gui.ui_specification.implementation.gui_main_desing import *


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

        # TODO: Delete
        self.__load_json_input("tests/cli/input-example-thermal-aperiodics-energy.json")

    def simulate_thermal_state_changed(self, state: bool):
        print("State changed")
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
        if input_object["simulate_thermal"]:
            # Fill simulation tab fields
            self.checkBox_simulation_thermal.setChecked(True)

            tcpn_model_names = TCPNThermalModelSelector.get_tcpn_model_names()

            self.comboBox_simulation_energy_model.setCurrentIndex(
                tcpn_model_names.index(input_object["tasks_specification"]["task_consumption_model"]))

            self.doubleSpinBox_simulation_mesh_step.setValue(input_object["simulation_specification"]["mesh_step"])

            self.doubleSpinBox_simulation_accuracy.setValue(input_object["simulation_specification"]["dt"])

        else:
            self.checkBox_simulation_thermal.setChecked(False)

        # Fill tasks tab fields
        if input_object["tasks_specification"]["task_generation_system"] == "Manual":
            tasks = input_object["tasks_specification"]["tasks"]
            for i in range(len(tasks)):
                new_row = [tasks[i]["type"],
                           tasks[i]["worst_case_execution_time"],
                           tasks[i].get("arrive"),
                           tasks[i].get("period") if tasks[i]["type"] == "Periodic" else tasks[i].get("deadline"),
                           tasks[i].get("energy_consumption")
                           ]
                self.__add_new_row_to_table_widget(self.tableWidget_tasks_list, new_row)

        # Fill CPU tab fields
        # Fill core tab fields
        for i in input_object["cpu_specification"]["cores_specification"]["available_frequencies"]:
            self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_avaliable_frequencies, [i])

        for i in input_object["cpu_specification"]["cores_specification"]["cores_frequencies"]:
            self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_selected_frequencies, [i])

        if input_object["simulate_thermal"]:
            automatic_origins = input_object["cpu_specification"]["cores_specification"]["cores_origins"] == "Automatic"
            self.checkBox_cpu_cores_automatic_origins.setChecked(automatic_origins)
            if not automatic_origins:
                for i in input_object["cpu_specification"]["cores_specification"]["cores_origins"]:
                    self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_origins_list, [i["x"], i["y"]])

            # Fill energy tab
            self.doubleSpinBox_cpu_cores_energy_dynamic_alpha.setValue(
                input_object["cpu_specification"]["cores_specification"]["energy_consumption_properties"][
                    "dynamic_alpha"])

            self.doubleSpinBox_cpu_cores_energy_dynamic_beta.setValue(
                input_object["cpu_specification"]["cores_specification"]["energy_consumption_properties"][
                    "dynamic_beta"])

            self.doubleSpinBox_cpu_cores_energy_leakage_alpha.setValue(
                input_object["cpu_specification"]["cores_specification"]["energy_consumption_properties"][
                    "leakage_alpha"])

            self.doubleSpinBox_cpu_cores_energy_leakage_delta.setValue(
                input_object["cpu_specification"]["cores_specification"]["energy_consumption_properties"][
                    "leakage_delta"])

            # Fill physical tab
            self.doubleSpinBox_cpu_cores_physical_x.setValue(
                input_object["cpu_specification"]["cores_specification"]["physical_properties"]["x"])

            self.doubleSpinBox_cpu_cores_physical_y.setValue(
                input_object["cpu_specification"]["cores_specification"]["physical_properties"]["y"])

            self.doubleSpinBox_cpu_cores_physical_z.setValue(
                input_object["cpu_specification"]["cores_specification"]["physical_properties"]["z"])

            self.doubleSpinBox_cpu_cores_physical_p.setValue(
                input_object["cpu_specification"]["cores_specification"]["physical_properties"]["density"])

            self.doubleSpinBox_cpu_cores_physical_c_p.setValue(
                input_object["cpu_specification"]["cores_specification"]["physical_properties"][
                    "specific_heat_capacity"])

            self.doubleSpinBox_cpu_cores_physical_k.setValue(
                input_object["cpu_specification"]["cores_specification"]["physical_properties"]["thermal_conductivity"])

            # Fill board tab fields
            # Fill physical tab
            self.doubleSpinBox_cpu_board_physical_x.setValue(
                input_object["cpu_specification"]["board_specification"]["physical_properties"]["x"])

            self.doubleSpinBox_cpu_board_physical_y.setValue(
                input_object["cpu_specification"]["board_specification"]["physical_properties"]["y"])

            self.doubleSpinBox_cpu_board_physical_z.setValue(
                input_object["cpu_specification"]["board_specification"]["physical_properties"]["z"])

            self.doubleSpinBox_cpu_board_physical_p.setValue(
                input_object["cpu_specification"]["board_specification"]["physical_properties"]["density"])

            self.doubleSpinBox_cpu_board_physical_c_p.setValue(
                input_object["cpu_specification"]["board_specification"]["physical_properties"][
                    "specific_heat_capacity"])

            self.doubleSpinBox_cpu_board_physical_k.setValue(
                input_object["cpu_specification"]["board_specification"]["physical_properties"]["thermal_conductivity"])

        # Fill environment tab fields
        if input_object["simulate_thermal"]:
            self.doubleSpinBox_environment_env_temperature.setValue(
                input_object["environment_specification"]["environment_temperature"])
            self.doubleSpinBox_environment_max_temperature.setValue(
                input_object["environment_specification"]["maximum_temperature"])
            self.doubleSpinBox_environment_convection_factor.setValue(
                input_object["environment_specification"]["convection_factor"])

        # Fill scheduler tab fields
        scheduler_names = SchedulerSelector.get_scheduler_names()

        self.comboBox_scheduler_select.setCurrentIndex(
            scheduler_names.index(input_object["scheduler_specification"]["name"]))

        # Fill output tab fields
        self.label_output_path.setText(input_object["output_specification"]["output_path"])
        self.lineEdit_output_base_naming.setText(input_object["output_specification"]["output_naming"])
        for i in input_object["output_specification"]["selected_output"]:
            self.__add_new_row_to_table_widget(self.tableWidget_output_selected_drawers, [i])

    @staticmethod
    def __add_new_row_to_table_widget(table_widget: QtWidgets.QTableWidget, new_row: list):
        """
        Add row to table widget
        :param table_widget: Table widget where add the row
        :param new_row: New row with Nones in empty columns
        """
        actual_size = table_widget.rowCount()
        table_widget.setRowCount(actual_size + 1)

        for i in range(len(new_row)):
            if new_row[i] is not None:
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(new_row[i]))
                table_widget.setItem(actual_size, i, item)

    @staticmethod
    def __delete_selected_row_from_table_widget(table_widget: QtWidgets.QTableWidget):
        """
        Delete the selected row from the table widget
        :param table_widget: Table widget where add the row
        """
        current_selected_row = table_widget.currentRow()
        if current_selected_row != -1:
            table_widget.removeRow(current_selected_row)

    def start_simulation(self):
        # TODO: Save as JSON
        # TODO: Use the JSON in the same way as CLI
        print("start_simulation")

    def add_task(self):
        # TODO
        print("add_task")
        self.__add_new_row_to_table_widget(self.tableWidget_tasks_list, [12, None, 12, None, 12])

    def delete_task(self):
        self.__delete_selected_row_from_table_widget(self.tableWidget_tasks_list)

    def generate_automatic_tasks(self):
        # TODO
        print("generate_automatic_tasks")

    def add_origin(self):
        # TODO
        print("add_origin")

    def delete_origin(self):
        self.__delete_selected_row_from_table_widget(self.tableWidget_cpu_cores_origins_list)

    def add_available_frequency(self):
        # TODO
        print("add_available_frequency")

    def delete_available_frequency(self):
        self.__delete_selected_row_from_table_widget(self.tableWidget_cpu_cores_avaliable_frequencies)

    def add_selected_frequency(self):
        # TODO
        print("add_selected_frequency")

    def delete_selected_frequency(self):
        self.__delete_selected_row_from_table_widget(self.tableWidget_cpu_cores_selected_frequencies)

    def add_output(self):
        # TODO
        print("add_output")

    def delete_output(self):
        self.__delete_selected_row_from_table_widget(self.tableWidget_output_selected_drawers)

    def generate_automatic_origins_changed(self, state: bool):
        # Control automatic origins enabled/disabled
        self.tab_cpu_cores_origins.setEnabled(not state)

    def change_output_path(self):
        # TODO: Open browser to search output
        print("change_output_path")

    def get_data(self):
        # TODO
        pass
