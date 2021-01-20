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
        # Assuming homogeneous CPU
        common_core_specification = cpu_specification.cores_definition[0].core_type

        consumption_by_cpu = [
            (common_core_specification.core_energy_consumption.dynamic_alpha * (f ** 3) +
             common_core_specification.core_energy_consumption.dynamic_beta) for f in
            clock_relative_frequencies for _ in
            range(len(cpu_specification.cores_definition))]

        return numpy.repeat(numpy.asarray(consumption_by_cpu).reshape((-1, 1)),
                            len(task_set.periodic_tasks) + len(task_set.aperiodic_tasks), axis=1)
