import json
from typing import Dict, List, Tuple, Optional

import jsonschema
from jsonschema import ValidationError

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.environment_specification.EnvironmentSpecification import EnvironmentSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.simulation_specification.TCPNModelSpecification import TCPNModelSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.schedulers.templates.abstract_scheduler.AbstractScheduler import AbstractScheduler
from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


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

    @staticmethod
    def validate_input(input_json: Dict, schema_json: Dict) -> [bool, str]:
        # Validate the input
        # TODO: Fix to allow reference in input
        try:
            jsonschema.validate(input_json, schema_json)
            return False, ""
        except ValidationError as ve:
            print()
            return True, 'Error: Wrong fields validation in ' + '/'.join(map(lambda x: str(x), ve.absolute_path)) + \
                   ' with message ' + ve.message

    @staticmethod
    def __obtain_tasks_specification(input_json: Dict) -> [TasksSpecification, Dict]:
        tasks_specification = input_json["tasks_specification"]
        task_generation_system = tasks_specification["task_generation_system"]
        task_consumption_model = tasks_specification["task_consumption_model"]

        if task_generation_system == "Manual":
            tasks = tasks_specification["tasks"]
            for i in tasks:
                type_of_task = tasks["type"]
                worst_case_execution_time = int(tasks["worst_case_execution_time"])

                if task_consumption_model == "Energy based":
                    # Energy based task
                    energy_consumption = float(tasks["energy_consumption"])
                else:
                    # Frequency based tasks
                    energy_consumption = None

                if type_of_task == "Periodic":
                    # Periodic task
                    period = float(tasks["period"])
                else:
                    # Aperiodic task
                    arrive = float(tasks["arrive"])
                    deadline = float(tasks["deadline"])
        pass

    @staticmethod
    def __obtain_cpu_specification(input_json: Dict) -> [CpuSpecification, Dict]:
        pass

    @staticmethod
    def __obtain_environment_specification(input_json: Dict) -> [EnvironmentSpecification, Dict]:
        pass

    @staticmethod
    def __obtain_simulation_specification(input_json: Dict) -> [SimulationSpecification, Dict]:
        pass

    @staticmethod
    def __obtain_tcpn_model_specification(input_json: Dict) -> [TCPNModelSpecification, Dict]:
        pass

    @staticmethod
    def __obtain_scheduler_specification(input_json: Dict) -> [AbstractScheduler, Dict]:
        pass

    @staticmethod
    def __obtain_output_specification(input_json: Dict) -> [List[Tuple[AbstractResultDrawer, Dict[str, str]]], Dict]:
        pass

    @classmethod
    def obtain_global_model(cls, input_json: Dict) -> [GlobalSpecification, AbstractScheduler,
                                                       List[Tuple[AbstractResultDrawer, Dict[str, str]]], Dict]:

        tasks_specification, input_json = cls.__obtain_tasks_specification(input_json)

        cpu_specification, input_json = cls.__obtain_cpu_specification(input_json)

        environment_specification, input_json = cls.__obtain_environment_specification(input_json)

        simulation_specification, input_json = cls.__obtain_simulation_specification(input_json)

        tcpn_model_specification, input_json = cls.__obtain_tcpn_model_specification(input_json)

        scheduler_specification, input_json = cls.__obtain_scheduler_specification(input_json)

        output_specification, input_json = cls.__obtain_output_specification(input_json)

        global_specification = GlobalSpecification(tasks_specification, cpu_specification, environment_specification,
                                                   simulation_specification, tcpn_model_specification)

        return global_specification, scheduler_specification, output_specification, input_json
