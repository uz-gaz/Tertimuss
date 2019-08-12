import json
import os
import threading

from PyQt5.QtWidgets import QFileDialog

from main.core.tcpn_model_generator.GlobalModel import GlobalModel
from main.ui.common.JSONGlobalModelParser import JSONGlobalModelParser
from main.ui.common.SchedulerSelector import SchedulerSelector
from main.ui.common.TCPNThermalModelSelector import TCPNThermalModelSelector
from main.ui.common.TaskGeneratorSelector import TaskGeneratorSelector
from main.ui.gui.implementation.AddAutomaticTaskDialog import AddAutomaticTaskDialog
from main.ui.gui.implementation.AddFrequencyDialog import AddFrequencyDialog
from main.ui.gui.implementation.AddOriginDialog import AddOriginDialog
from main.ui.gui.implementation.AddOutputDialog import AddOutputDialog
from main.ui.gui.implementation.AddTaskDialog import AddTaskDialog
from main.ui.gui.ui_specification.implementation.gui_main_desing import *


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        """
        Main GUI window
        """
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # Energy generation model
        tcpn_model_names = TCPNThermalModelSelector.get_tcpn_model_names()

        for i in range(len(tcpn_model_names)):
            self.comboBox_simulation_energy_model.addItem("")
            self.comboBox_simulation_energy_model.setItemText(i, tcpn_model_names[i])

        # Available schedulers
        scheduler_names = SchedulerSelector.get_scheduler_names()

        for i in range(len(scheduler_names)):
            self.comboBox_scheduler_select.addItem("")
            self.comboBox_scheduler_select.setItemText(i, scheduler_names[i])

    def simulate_thermal_state_changed(self, state: bool):
        """
        Simulate thermal checkbox's state change listener
        :param state: True if checked, False if not
        """
        # Control thermal enabled/disabled
        self.doubleSpinBox_simulation_mesh_step.setEnabled(state)
        self.comboBox_simulation_energy_model.setEnabled(state)
        self.tab_environment.setEnabled(state)
        self.tab_board.setEnabled(state)
        self.tab_cpu_cores_physical.setEnabled(state)
        self.tab_cpu_cores_origins.setEnabled(state)
        self.tab_cpu_cores_energy.setEnabled(state)
        self.checkBox_cpu_cores_automatic_origins.setEnabled(state)

    def load_json(self):
        """
        Load JSON button's click listener
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load specification", "", "JSON (*.json)",
                                                   options=options)
        if file_name:
            self.__load_json_input(file_name)

    def __load_json_input(self, path: str):
        """
        Load JSON object from path and if is valid fill all fields
        :param path: Path where JSON object is stored
        """
        # Path of the input validate schema
        input_schema_path = '../../cli/input_schema/input-schema.json'
        absolute_input_schema_path = os.path.join(os.path.dirname(__file__), input_schema_path)

        # Read schema
        error, message, schema_object = JSONGlobalModelParser.read_input(absolute_input_schema_path)

        if error:
            self.label_status.setText("Status:" + message)

        # Read input
        error, message, input_object = JSONGlobalModelParser.read_input(path)

        if error:
            self.label_status.setText("Status:" + message)

        # Validate schema
        error, message = JSONGlobalModelParser.validate_input(input_object, schema_object)

        if error:
            self.label_status.setText("Status:" + message)

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
        else:
            period_start = input_object["tasks_specification"]["automatic_generation"]["interval_for_periods"][
                "min_period"]
            period_end = input_object["tasks_specification"]["automatic_generation"]["interval_for_periods"][
                "max_period"]
            number_of_tasks = input_object["tasks_specification"]["automatic_generation"]["number_of_tasks"]
            utilization = input_object["tasks_specification"]["automatic_generation"]["utilization_of_the_task_set"]
            generator_algorithm = TaskGeneratorSelector.select_task_generator(
                input_object["tasks_specification"]["automatic_generation"]["name"])

            tasks = generator_algorithm.generate({
                "number_of_tasks": number_of_tasks,
                "utilization": utilization,
                "min_period_interval": period_start,
                "max_period_interval": period_end,
                "processor_frequency": 1
            })

            for task in tasks:
                self.__add_new_row_to_table_widget(self.tableWidget_tasks_list,
                                                   ["Periodic", task.c, None, task.d,
                                                    task.e if self.checkBox_simulation_thermal.isChecked() else None])

        # Fill CPU tab fields
        # Fill core tab fields
        for i in input_object["cpu_specification"]["cores_specification"]["available_frequencies"]:
            self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_available_frequencies, [i])

        for i in input_object["cpu_specification"]["cores_specification"]["operating_frequencies"]:
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

    @staticmethod
    def __check_duplicated_row_from_table_widget(table_widget: QtWidgets.QTableWidget, value_to_search: str) -> bool:
        """
        Check if the value value_to_search is in the table table_widget
        :param table_widget: Table widget where add the row
        """
        item_list = []
        for i in range(table_widget.rowCount()):
            item = table_widget.item(i, 0)
            item_list.append(item.text())
        return any([i == value_to_search for i in item_list])

    def start_simulation(self):
        """
        Start simulation button's click listener
        """
        thermal_simulation = self.checkBox_simulation_thermal.isChecked()

        task_consumption_model = self.comboBox_simulation_energy_model.currentText()

        tasks_as_json = [{
                             "type": "Periodic",
                             "worst_case_execution_time": int(self.tableWidget_tasks_list.item(i, 1).text()),
                             "period": float(self.tableWidget_tasks_list.item(i, 3).text()),
                             "energy_consumption": float(self.tableWidget_tasks_list.item(i, 4).text())
                         } if self.tableWidget_tasks_list.item(i, 0).text() == "Periodic" else
                         {
                             "type": "Aperiodic",
                             "worst_case_execution_time": int(self.tableWidget_tasks_list.item(i, 1).text()),
                             "arrive": float(self.tableWidget_tasks_list.item(i, 2).text()),
                             "deadline": float(self.tableWidget_tasks_list.item(i, 3).text()),
                             "energy_consumption": float(self.tableWidget_tasks_list.item(i, 4).text())
                         } for i in range(
            self.tableWidget_tasks_list.rowCount())] if thermal_simulation and task_consumption_model == "Energy based" \
            else [{
                      "type": "Periodic",
                      "worst_case_execution_time": int(self.tableWidget_tasks_list.item(i, 1).text()),
                      "period": float(self.tableWidget_tasks_list.item(i, 3).text())
                  } if self.tableWidget_tasks_list.item(i, 0).text() == "Periodic" else
                  {
                      "type": "Aperiodic",
                      "worst_case_execution_time": int(self.tableWidget_tasks_list.item(i, 1).text()),
                      "arrive": float(self.tableWidget_tasks_list.item(i, 2).text()),
                      "deadline": float(self.tableWidget_tasks_list.item(i, 3).text())
                  } for i in range(self.tableWidget_tasks_list.rowCount())]

        available_frequencies = [int(self.tableWidget_cpu_cores_available_frequencies.item(i, 0).text()) for i in
                                 range(self.tableWidget_cpu_cores_available_frequencies.rowCount())]

        operating_frequencies = [int(self.tableWidget_cpu_cores_selected_frequencies.item(i, 0).text()) for i in
                             range(self.tableWidget_cpu_cores_selected_frequencies.rowCount())]

        cores_origins = [{"x": float(self.tableWidget_cpu_cores_origins_list.item(i, 0).text()),
                          "y": float(self.tableWidget_cpu_cores_origins_list.item(i, 1).text())} for i in
                         range(self.tableWidget_cpu_cores_origins_list.rowCount())] \
            if not self.checkBox_cpu_cores_automatic_origins.isChecked() else "Automatic"

        selected_output = [self.tableWidget_output_selected_drawers.item(i, 0).text() for i in
                           range(self.tableWidget_output_selected_drawers.rowCount())]

        data_as_json = {
            "simulate_thermal": True,
            "tasks_specification": {
                "task_generation_system": "Manual",
                "task_consumption_model": task_consumption_model,
                "tasks": tasks_as_json
            },
            "cpu_specification": {
                "board_specification": {
                    "physical_properties": {
                        "x": self.doubleSpinBox_cpu_board_physical_x.value(),
                        "y": self.doubleSpinBox_cpu_board_physical_y.value(),
                        "z": self.doubleSpinBox_cpu_board_physical_z.value(),
                        "density": self.doubleSpinBox_cpu_board_physical_p.value(),
                        "specific_heat_capacity": self.doubleSpinBox_cpu_board_physical_c_p.value(),
                        "thermal_conductivity": self.doubleSpinBox_cpu_board_physical_k.value()
                    }
                },
                "cores_specification": {
                    "physical_properties": {
                        "x": self.doubleSpinBox_cpu_cores_physical_x.value(),
                        "y": self.doubleSpinBox_cpu_cores_physical_y.value(),
                        "z": self.doubleSpinBox_cpu_cores_physical_z.value(),
                        "density": self.doubleSpinBox_cpu_cores_physical_p.value(),
                        "specific_heat_capacity": self.doubleSpinBox_cpu_cores_physical_c_p.value(),
                        "thermal_conductivity": self.doubleSpinBox_cpu_cores_physical_k.value()
                    },
                    "energy_consumption_properties": {
                        "leakage_alpha": self.doubleSpinBox_cpu_cores_energy_leakage_alpha.value(),
                        "leakage_delta": self.doubleSpinBox_cpu_cores_energy_leakage_delta.value(),
                        "dynamic_alpha": self.doubleSpinBox_cpu_cores_energy_dynamic_alpha.value(),
                        "dynamic_beta": self.doubleSpinBox_cpu_cores_energy_dynamic_beta.value()
                    },
                    "available_frequencies": available_frequencies,
                    "operating_frequencies": operating_frequencies,
                    "cores_origins": cores_origins
                }
            },
            "environment_specification": {
                "environment_temperature": self.doubleSpinBox_environment_env_temperature.value(),
                "maximum_temperature": self.doubleSpinBox_environment_max_temperature.value(),
                "convection_factor": self.doubleSpinBox_environment_convection_factor.value()
            },
            "output_specification": {
                "output_path": self.label_output_path.text(),
                "output_naming": self.lineEdit_output_base_naming.text(),
                "selected_output": selected_output
            },
            "scheduler_specification": {
                "name": self.comboBox_scheduler_select.currentText()
            },
            "simulation_specification": {
                "mesh_step": self.doubleSpinBox_simulation_mesh_step.value(),
                "dt": self.doubleSpinBox_simulation_accuracy.value()
            }
        } if thermal_simulation else \
            {
                "simulate_thermal": False,
                "tasks_specification": {
                    "task_generation_system": "Manual",
                    "tasks": tasks_as_json
                },
                "cpu_specification": {
                    "cores_specification": {
                        "available_frequencies": available_frequencies,
                        "operating_frequencies": operating_frequencies
                    }
                },
                "output_specification": {
                    "output_path": self.label_output_path.text(),
                    "output_naming": self.lineEdit_output_base_naming.text(),
                    "selected_output": selected_output
                },
                "scheduler_specification": {
                    "name": self.comboBox_scheduler_select.currentText()
                },
                "simulation_specification": {
                    "dt": self.doubleSpinBox_simulation_accuracy.value()
                }
            }

        # Execute simulation
        # FIXME: The simulation will end even if the window is closed
        simulator_thread = threading.Thread(target=(lambda: self.__execute_simulation(data_as_json)))
        simulator_thread.start()

    def __execute_simulation(self, input_object):
        """
        Execute simulation from JSON
        :param input_object: Simulation which will be executed
        """
        # Get tabs status
        enable_tab_simulation = self.tab_simulation.isEnabled()
        enable_tab_tasks = self.tab_tasks.isEnabled()
        enable_tab_environment = self.tab_environment.isEnabled()
        enable_tab_cpu = self.tab_cpu.isEnabled()
        enable_tab_scheduler = self.tab_scheduler.isEnabled()
        enable_tab_output = self.tab_output.isEnabled()

        # Disable all tabs
        self.tab_simulation.setEnabled(False)
        self.tab_tasks.setEnabled(False)
        self.tab_environment.setEnabled(False)
        self.tab_cpu.setEnabled(False)
        self.tab_scheduler.setEnabled(False)
        self.tab_output.setEnabled(False)

        # Status Busy
        self.label_status.setText("Status: Processing data")

        # Path of the input validate schema
        input_schema_path = '../../cli/input_schema/input-schema.json'
        absolute_input_schema_path = os.path.join(os.path.dirname(__file__), input_schema_path)

        # Read schema
        error, message, schema_object = JSONGlobalModelParser.read_input(absolute_input_schema_path)

        if not error:
            # Validate schema
            error, message = JSONGlobalModelParser.validate_input(input_object, schema_object)
        else:
            self.label_status.setText("Status:" + message)

        if not error:
            # Get model and scheduler
            global_specification, scheduler, output_path, output_list, scenario_description_completed = \
                JSONGlobalModelParser.obtain_global_model(input_object)

            # Create output directory if not exist
            os.makedirs(output_path, exist_ok=True)

            # Create global model
            try:

                self.label_status.setText("Status: Creating simulation")

                global_model = GlobalModel(global_specification)

                self.label_status.setText("Status: Running simulation")

                scheduler_result = scheduler.simulate(global_specification, global_model, None)

                self.label_status.setText("Status: Saving output")

                # Plot scheduler result
                for i in output_list:
                    output_drawer, options = i
                    output_drawer.plot(global_specification, scheduler_result, options)

                # Save JSON if needed
                if self.checkBox_simulation_save.isChecked():
                    output_path = input_object["output_specification"]["output_path"]
                    output_naming = input_object["output_specification"]["output_naming"] + "_specification.json"
                    with open(os.path.join(output_path, output_naming), 'w') as f:
                        json.dump(input_object, f, indent=4)

                self.label_status.setText("Status: Simulation finished")

            except Exception:
                self.label_status.setText("Error while solving the problem")
        else:
            self.label_status.setText("Status:" + message)

        # Enable all tabs
        self.tab_simulation.setEnabled(enable_tab_simulation)
        self.tab_tasks.setEnabled(enable_tab_tasks)
        self.tab_environment.setEnabled(enable_tab_environment)
        self.tab_cpu.setEnabled(enable_tab_cpu)
        self.tab_scheduler.setEnabled(enable_tab_scheduler)
        self.tab_output.setEnabled(enable_tab_output)

    def add_task(self):
        """
        Add task button's click listener
        """
        is_thermal_enabled = self.checkBox_simulation_thermal.isChecked()
        is_energy_enabled = self.comboBox_simulation_energy_model.currentText() == "Energy based"
        dialog_ui = AddTaskDialog(is_thermal_enabled, is_energy_enabled, self)
        dialog_ui.exec()
        return_value = dialog_ui.get_return_value()
        if return_value is not None:
            self.__add_new_row_to_table_widget(self.tableWidget_tasks_list, return_value)

    def delete_task(self):
        """
        Delete task button's click listener
        """
        self.__delete_selected_row_from_table_widget(self.tableWidget_tasks_list)

    def generate_automatic_tasks(self):
        """
        Generate automatic tasks button's click listener
        """
        dialog_ui = AddAutomaticTaskDialog(self)
        dialog_ui.exec()
        return_value = dialog_ui.get_return_value()
        if return_value is not None and return_value[0] < return_value[1]:
            period_start = return_value[0]
            period_end = return_value[1]
            number_of_tasks = return_value[2]
            utilization = return_value[3]
            algorithm_name = return_value[4]
            generator_algorithm = TaskGeneratorSelector.select_task_generator(algorithm_name)

            tasks = generator_algorithm.generate({
                "number_of_tasks": number_of_tasks,
                "utilization": utilization,
                "min_period_interval": period_start,
                "max_period_interval": period_end,
                "processor_frequency": 1
            })

            for task in tasks:
                self.__add_new_row_to_table_widget(self.tableWidget_tasks_list,
                                                   ["Periodic", task.c, None, task.d,
                                                    task.e if self.checkBox_simulation_thermal.isChecked() else None])

    def add_origin(self):
        """
        Add origin button's click listener
        """
        dialog_ui = AddOriginDialog(self)
        dialog_ui.exec()
        return_value = dialog_ui.get_return_value()
        if return_value is not None:
            self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_origins_list, return_value)

    def delete_origin(self):
        """
        Delete origin button's click listener
        """
        self.__delete_selected_row_from_table_widget(self.tableWidget_cpu_cores_origins_list)

    def add_available_frequency(self):
        """
        Add available frequency button's click listener
        """
        dialog_ui = AddFrequencyDialog(self)
        dialog_ui.exec()
        return_value = dialog_ui.get_return_value()
        if return_value is not None and not self.__check_duplicated_row_from_table_widget(
                self.tableWidget_cpu_cores_available_frequencies, str(return_value[0])):
            self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_available_frequencies, return_value)

    def delete_available_frequency(self):
        """
        Delete available frequency button's click listener
        """
        self.__delete_selected_row_from_table_widget(self.tableWidget_cpu_cores_available_frequencies)

    def add_selected_frequency(self):
        """
        Add selected frequency button's click listener
        """
        dialog_ui = AddFrequencyDialog(self)
        dialog_ui.exec()
        return_value = dialog_ui.get_return_value()
        if return_value is not None:
            self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_selected_frequencies, return_value)

    def delete_selected_frequency(self):
        """
        Delete selected frequency button's click listener
        """
        self.__delete_selected_row_from_table_widget(self.tableWidget_cpu_cores_selected_frequencies)

    def add_output(self):
        """
        Add output button's click listener
        """
        is_thermal_enabled = self.checkBox_simulation_thermal.isChecked()
        dialog_ui = AddOutputDialog(is_thermal_enabled, self)
        dialog_ui.exec()
        return_value = dialog_ui.get_return_value()
        if return_value is not None and not self.__check_duplicated_row_from_table_widget(
                self.tableWidget_output_selected_drawers, str(return_value[0])):
            self.__add_new_row_to_table_widget(self.tableWidget_output_selected_drawers, return_value)
            self.tableWidget_output_selected_drawers.sortItems(0)

    def delete_output(self):
        """
        Delete output button's click listener
        """
        self.__delete_selected_row_from_table_widget(self.tableWidget_output_selected_drawers)

    def generate_automatic_origins_changed(self, state: bool):
        """
        Generate automatic origins checkbox's state change listener
        :param state: True if checked, False if not
        """
        # Control automatic origins enabled/disabled
        self.tab_cpu_cores_origins.setEnabled(not state)

    def change_output_path(self):
        """
        Change output path button's click listener
        """
        file_name = QFileDialog.getExistingDirectory(self, "Output path")

        if file_name is not None:
            self.label_output_path.setText(file_name)
