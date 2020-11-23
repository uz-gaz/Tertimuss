from typing import List, Union

import numpy

from ._thermal_model import ThermalModel
from tertimuss_simulation_lib.system_definition import HomogeneousCpuSpecification, TaskSet


class ThermalModelFrequencyAware(ThermalModel):
    """
    Thermal model where cpu frequency is used to simulate the tasks heat generation
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

        n: int = len(task_set.periodic_tasks) + len(task_set.aperiodic_tasks)

        consumption_by_cpu = [
            (cpu_specification.cores_specification.energy_consumption_properties.dynamic_alpha * (f ** 3) +
             cpu_specification.cores_specification.energy_consumption_properties.dynamic_beta) for f in
            clock_relative_frequencies]

        return numpy.repeat(numpy.asarray(consumption_by_cpu).reshape((-1, 1)), n, axis=1)
