from typing import List, Union

import numpy

from ._thermal_model import ThermalModel
from tertimuss.simulation_lib.system_definition import HomogeneousCpuSpecification, TaskSet, Task


class ThermalModelEnergy(ThermalModel):
    """
    Thermal model where task energy consumption is used to simulate the tasks heat generation
    """

    @staticmethod
    def _get_dynamic_power_consumption(cpu_specification: Union[HomogeneousCpuSpecification],
                                       task_set: TaskSet,
                                       clock_relative_frequencies: List[float]) -> numpy.ndarray:
        """
        Method to implement. Return an array with shape (m , n). Each place contains the weight in the
        arcs t_exec_n -> cpu_m

        :param cpu_specification: Cpu specification
        :param task_set: Tasks specification
        :param clock_relative_frequencies: Core frequencies
        :return: an array with shape (m , n). Each place contains the weight in the arcs t_exec_n -> cpu_m
        """

        tasks: List[Task] = task_set.periodic_tasks + task_set.aperiodic_tasks

        consumption_by_task = [task.energy_consumption for task in tasks]

        m = cpu_specification.cores_specification.number_of_cores

        return numpy.repeat(numpy.asarray(consumption_by_task).reshape((1, -1)), m, axis=0)
