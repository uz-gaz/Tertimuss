import json
import os
from typing import Dict, List, Tuple, Optional

import jsonref
import jsonschema
from jsonschema import ValidationError

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.cpu_specification.BoardSpecification import BoardSpecification
from main.core.problem_specification.cpu_specification.CoreGroupSpecification import CoreGroupSpecification
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.cpu_specification.EnergyConsumptionProperties import EnergyConsumptionProperties
from main.core.problem_specification.cpu_specification.MaterialCuboid import MaterialCuboid
from main.core.problem_specification.cpu_specification.Origin import Origin
from main.core.problem_specification.environment_specification.EnvironmentSpecification import EnvironmentSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.simulation_specification.TCPNModelSpecification import TCPNModelSpecification
from main.core.problem_specification.tasks_specification.AperiodicTask import AperiodicTask
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.tasks_specification.Task import Task
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.schedulers.templates.abstract_scheduler.AbstractScheduler import AbstractScheduler
from main.core.tcpn_model_generator.ThermalModelSelector import ThermalModelSelector
from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer
from main.ui.common.OutputSelector import OutputSelector
from main.ui.common.SchedulerSelector import SchedulerSelector
from main.ui.common.TCPNThermalModelSelector import TCPNThermalModelSelector
from main.ui.common.TaskGeneratorSelector import TaskGeneratorSelector


class JSONGlobalModelParser(object):
    @staticmethod
    def read_input(input_path) -> [bool, str, Optional[Dict]]:
        try:
            with open(input_path, "r") as read_file:
                try:
                    input_schema = json.load(read_file)
                    return False, "", input_schema
                except ValueError:
                    return True, "Error: Wrong json file syntax", None
        except IOError:
            return True, "Error: Can't read the file " + input_path, None

    @classmethod
    def read_input_with_references(cls, input_path) -> [bool, str, Optional[Dict]]:
        # relative_schema_path = os.path.join(schema_base_path, schema_name)
        # absolute_schema_path = os.path.join(os.path.dirname(__file__), relative_schema_path)
        try:
            with open(input_path, "r") as read_file:
                try:
                    input_schema: Dict = jsonref.load(read_file)
                    return False, "", input_schema
                except ValueError:
                    return True, "Error: Wrong json file syntax", None
        except IOError:
            return True, "Error: Can't read the file " + input_path, None

    @staticmethod
    def validate_input(input_json: Dict, schema_json: Dict) -> [bool, str]:
        # Validate the input
        try:
            jsonschema.validate(input_json, schema_json)
            return False, ""
        except ValidationError as ve:
            return True, 'Error: Wrong fields validation in ' + '/'.join(map(lambda x: str(x), ve.absolute_path)) + \
                   ' with message ' + ve.message

    @staticmethod
    def __obtain_tasks_specification(input_json: Dict) -> [TasksSpecification, Dict]:
        """
        Obtain tasks specification from input_json

        :param input_json: Json specification
        """
        # Make a copy of the json spec
        input_json = input_json.copy()

        tasks_specification = input_json["tasks_specification"]
        task_generation_system = tasks_specification["task_generation_system"]
        simulate_thermal = input_json["simulate_thermal"]

        # List of tasks to return
        tasks_list: List[Task] = []

        if task_generation_system == "Manual":
            # Manual task generation
            tasks = tasks_specification["tasks"]
            for task in tasks:
                type_of_task = task["type"]
                worst_case_execution_time = task["worst_case_execution_time"]

                if simulate_thermal and tasks_specification["task_consumption_model"] == "Energy based":
                    # Energy based task
                    energy_consumption = task["energy_consumption"]
                else:
                    # Frequency based tasks
                    energy_consumption = None

                if type_of_task == "Periodic":
                    # Periodic task
                    period = task["period"]
                    new_task = PeriodicTask(worst_case_execution_time, period, period, energy_consumption)
                else:
                    # Aperiodic task
                    arrive = task["arrive"]
                    deadline = task["deadline"]
                    new_task = AperiodicTask(worst_case_execution_time, arrive, deadline, energy_consumption)

                tasks_list.append(new_task)
        else:
            # Automatic task generation
            automatic_generation = tasks_specification["automatic_generation"]

            available_core_frequencies = input_json["cpu_specification"]["cores_specification"]["available_frequencies"]

            available_core_frequencies.sort()

            options = {
                "number_of_tasks": automatic_generation["number_of_tasks"],
                "utilization": automatic_generation["utilization_of_the_task_set"],
                "min_period_interval": automatic_generation["interval_for_periods"]["min_period"],
                "max_period_interval": automatic_generation["interval_for_periods"]["max_period"],
                "processor_frequency": available_core_frequencies[-1]
            }

            name = automatic_generation["name"]

            task_generator = TaskGeneratorSelector.select_task_generator(name)

            tasks_list: List[PeriodicTask] = task_generator.generate(options)

            # Generate new JSON
            tasks = []
            for i in tasks_list:
                task = {
                    "type": "Periodic",
                    "worst_case_execution_time": i.c,
                    "period": i.d
                }

                if simulate_thermal and tasks_specification["task_consumption_model"] == "Energy based":
                    # Energy based task
                    task["energy_consumption"] = i.e

                tasks.append(task)

            task_spec = {
                "task_consumption_model": tasks_specification["task_consumption_model"],
                "task_generation_system": "Manual",  # New task generation system will be manual
                "tasks": tasks
            }

            input_json["tasks_specification"] = task_spec

        return TasksSpecification(tasks_list), input_json

    @staticmethod
    def __obtain_cpu_specification(input_json: Dict) -> [CpuSpecification, Dict]:
        """
        Obtain cpu specification from input_json

        :param input_json: Json specification
        """
        # Make a copy of the json spec
        input_json = input_json.copy()

        cpu_specification = input_json["cpu_specification"]
        simulate_thermal = input_json["simulate_thermal"]

        cores_specification = cpu_specification["cores_specification"]

        available_frequencies = cores_specification["available_frequencies"]

        operating_frequencies = cores_specification["operating_frequencies"]

        if simulate_thermal:
            board_specification = cpu_specification["board_specification"]

            board_physical_properties = board_specification["physical_properties"]

            board_material_cuboid = MaterialCuboid(board_physical_properties["x"],
                                                   board_physical_properties["y"],
                                                   board_physical_properties["z"],
                                                   board_physical_properties["density"],
                                                   board_physical_properties["specific_heat_capacity"],
                                                   board_physical_properties["thermal_conductivity"])

            cores_physical_properties = cores_specification["physical_properties"]

            cores_material_cuboid = MaterialCuboid(cores_physical_properties["x"],
                                                   cores_physical_properties["y"],
                                                   cores_physical_properties["z"],
                                                   cores_physical_properties["density"],
                                                   cores_physical_properties["specific_heat_capacity"],
                                                   cores_physical_properties["thermal_conductivity"])

            energy_consumption_properties = cores_specification["energy_consumption_properties"]

            energy_consumption = EnergyConsumptionProperties(energy_consumption_properties["leakage_alpha"],
                                                             energy_consumption_properties["leakage_delta"],
                                                             energy_consumption_properties["dynamic_alpha"],
                                                             energy_consumption_properties["dynamic_beta"]
                                                             )

            cores_origins = cores_specification["cores_origins"]

            if cores_origins == "Automatic":
                cores_origins = None
            else:
                cores_origins = [Origin(i["x"], i["y"]) for i in cores_origins]

            cpu_specification = CpuSpecification(
                BoardSpecification(board_material_cuboid),
                CoreGroupSpecification(cores_material_cuboid,
                                       energy_consumption,
                                       available_frequencies,
                                       operating_frequencies,
                                       cores_origins)
            )

            if cores_specification["cores_origins"] == "Automatic":
                cores_origins_automatic = cpu_specification.cores_specification.cores_origins
                core_origins_list = [{"x": i.x, "y": i.y} for i in cores_origins_automatic]
                input_json["cpu_specification"]["cores_specification"]["cores_origins"] = core_origins_list
        else:
            # This values won't be used during the simulation
            board_material_cuboid = MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400)
            cores_material_cuboid = MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148)
            energy_consumption = EnergyConsumptionProperties()

            cpu_specification = CpuSpecification(
                BoardSpecification(board_material_cuboid),
                CoreGroupSpecification(cores_material_cuboid,
                                       energy_consumption,
                                       available_frequencies,
                                       operating_frequencies,
                                       None))

        return cpu_specification, input_json

    @staticmethod
    def __obtain_environment_specification(input_json: Dict) -> [EnvironmentSpecification, Dict]:
        """
        Obtain environment specification from input_json

        :param input_json: Json specification
        """
        # Make a copy of the json spec
        input_json = input_json.copy()

        environment_specification = input_json["environment_specification"]
        simulate_thermal = input_json["simulate_thermal"]

        if simulate_thermal:
            environment_specification = EnvironmentSpecification(environment_specification["convection_factor"],
                                                                 environment_specification["environment_temperature"],
                                                                 environment_specification["maximum_temperature"])
        else:
            # This values won't be used during the simulation
            environment_specification = EnvironmentSpecification(0.001, 45, 110)

        return environment_specification, input_json

    @staticmethod
    def __obtain_simulation_specification(input_json: Dict) -> [SimulationSpecification, Dict]:
        """
        Obtain simulation specification from input_json

        :param input_json: Json specification
        """
        # Make a copy of the json spec
        input_json = input_json.copy()

        simulation_specification = input_json["simulation_specification"]
        simulate_thermal = input_json["simulate_thermal"]

        if simulate_thermal:
            simulation_specification = SimulationSpecification(simulation_specification["mesh_step"],
                                                               simulation_specification["dt"],
                                                               simulate_thermal)
        else:
            # This values won't be used during the simulation
            simulation_specification = SimulationSpecification(2,
                                                               simulation_specification["dt"],
                                                               simulate_thermal)

        return simulation_specification, input_json

    @staticmethod
    def __obtain_tcpn_model_specification(input_json: Dict) -> [TCPNModelSpecification, Dict]:
        """
        Obtain tcpn model specification from input_json

        :param input_json: Json specification
        """
        # Make a copy of the json spec
        input_json = input_json.copy()

        simulate_thermal = input_json["simulate_thermal"]

        if simulate_thermal:
            tasks_specification = input_json["tasks_specification"]
            tcpn_model_specification = tasks_specification["task_consumption_model"]
            tcpn_model_specification = TCPNModelSpecification(
                TCPNThermalModelSelector.select_tcpn_model(tcpn_model_specification))
        else:
            tcpn_model_specification = TCPNModelSpecification(ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

        return tcpn_model_specification, input_json

    @staticmethod
    def __obtain_scheduler_specification(input_json: Dict) -> [AbstractScheduler, Dict]:
        """
        Obtain scheduler specification from input_json

        :param input_json: Json specification
        """
        # Make a copy of the json spec
        input_json = input_json.copy()

        return SchedulerSelector.select_scheduler(input_json["scheduler_specification"]["name"]), input_json

    @staticmethod
    def __obtain_output_specification(input_json: Dict) -> [List[Tuple[AbstractResultDrawer, Dict[str, str]]],
                                                            str, Dict]:
        """
        Obtain tasks specification from input_json

        :param input_json: Json specification
        """
        # Make a copy of the json spec
        input_json = input_json.copy()

        output_list = []

        output_path = input_json["output_specification"]["output_path"]

        output_base_name = input_json["output_specification"]["output_naming"]

        selected_outputs = input_json["output_specification"]["selected_output"]

        for output_naming in selected_outputs:
            output_list.append((OutputSelector.select_output(output_naming), {
                "save_path": os.path.join(output_path, output_base_name +
                                          OutputSelector.select_output_naming(output_naming))}))

        return output_list, output_path, input_json

    @classmethod
    def obtain_global_model(cls, input_json: Dict) -> [GlobalSpecification, AbstractScheduler, str,
                                                       List[Tuple[AbstractResultDrawer, Dict[str, str]]], Dict]:

        tasks_specification, input_json = cls.__obtain_tasks_specification(input_json)

        cpu_specification, input_json = cls.__obtain_cpu_specification(input_json)

        environment_specification, input_json = cls.__obtain_environment_specification(input_json)

        simulation_specification, input_json = cls.__obtain_simulation_specification(input_json)

        tcpn_model_specification, input_json = cls.__obtain_tcpn_model_specification(input_json)

        scheduler_specification, input_json = cls.__obtain_scheduler_specification(input_json)

        output_specification, output_path, input_json = cls.__obtain_output_specification(input_json)

        global_specification = GlobalSpecification(tasks_specification, cpu_specification, environment_specification,
                                                   simulation_specification, tcpn_model_specification)

        return global_specification, scheduler_specification, output_path, output_specification, input_json
