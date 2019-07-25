import json
from typing import Dict, List, Tuple, Optional

import jsonschema
from jsonschema import ValidationError

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.environment_specification.EnvironmentSpecification import EnvironmentSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.simulation_specification.TCPNModelSpecification import TCPNModelSpecification
from main.core.problem_specification.tasks_specification.AperiodicTask import AperiodicTask
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.tasks_specification.Task import Task
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.schedulers.templates.abstract_scheduler.AbstractScheduler import AbstractScheduler
from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer
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

        # List of tasks to return
        tasks_list: List[Task] = []

        if task_generation_system == "Manual":
            # Manual task generation
            tasks = tasks_specification["tasks"]
            for task in tasks:
                type_of_task = task["type"]
                worst_case_execution_time = task["worst_case_execution_time"]

                if task_consumption_model == "Energy based":
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

            tasks_list = task_generator.generate(options)

        return tasks_list, input_json.copy()

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
