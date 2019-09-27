from typing import List

import scipy

from main.core.execution_simulator.system_modeling.ThermalModel import ThermalModel
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.problem_specification.tasks_specification.Task import Task


class ThermalModelEnergy(ThermalModel):
    """
    Thermal model where task energy consumption is used to simulate the tasks heat generation
    """

    @staticmethod
    def _get_dynamic_power_consumption(cpu_specification: CpuSpecification,
                                       tasks_specification: TasksSpecification,
                                       clock_relative_frequencies: List[float]) -> scipy.ndarray:
        """
        Method to implement. Return an array with shape (m , n). Each place contains the weight in the
        arcs t_exec_n -> cpu_m

        :param cpu_specification: Cpu specification
        :param tasks_specification: Tasks specification
        :param clock_relative_frequencies: Core frequencies
        :return: an array with shape (m , n). Each place contains the weight in the arcs t_exec_n -> cpu_m
        """

        tasks: List[Task] = tasks_specification.periodic_tasks + tasks_specification.aperiodic_tasks

        consumption_by_task = [task.e for task in tasks]

        m = len(cpu_specification.cores_specification.operating_frequencies)

        return scipy.repeat(scipy.asarray(consumption_by_task).reshape((1, -1)), m, axis=0)
