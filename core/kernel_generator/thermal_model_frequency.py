from typing import List

from core.kernel_generator.thermal_model import ThermalModel

import scipy

from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class ThermalModelFrequencyAware(ThermalModel):
    """
    Thermal model where cpu frequency is used to simulate the task heat generation
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
        rho = cpu_specification.cpu_core_specification.p
        cp = cpu_specification.cpu_core_specification.c_p
        v_cpu = cpu_specification.cpu_core_specification.z * cpu_specification.cpu_core_specification.x * \
                cpu_specification.cpu_core_specification.y / (1000 ** 3)

        n: int = len(tasks_specification.periodic_tasks) + len(tasks_specification.aperiodic_tasks)

        consumption_by_cpu = [
            (cpu_specification.dvfs_mult * (f ** 3) + cpu_specification.dvfs_const) / (v_cpu * rho * cp) for f in
            clock_relative_frequencies]

        return scipy.repeat(scipy.asarray(consumption_by_cpu).reshape((-1, 1)), n, axis=1)
