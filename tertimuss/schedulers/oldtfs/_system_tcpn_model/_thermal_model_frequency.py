from typing import List

import numpy

from ._thermal_model import ThermalModel
from tertimuss.simulation_lib.system_definition import ProcessorDefinition, TaskSet


class ThermalModelFrequencyAware(ThermalModel):
    """
    Thermal model where cpu frequency is used to simulate the tasks heat generation
    """

    @staticmethod
    def _get_dynamic_power_consumption(cpu_specification: ProcessorDefinition,
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

        n: int = len(task_set.periodic_tasks) + len(task_set.aperiodic_tasks)

        consumption_by_cpu = [
            (j.cores_specification.energy_consumption_properties.dynamic_alpha * (f ** 3) +
             j.cores_specification.energy_consumption_properties.dynamic_beta) for f in
            clock_relative_frequencies for _, j in
            sorted(cpu_specification.cores_definition.items(), key=lambda k: k[0])]

        return numpy.asarray(consumption_by_cpu).reshape((-1, 1))
