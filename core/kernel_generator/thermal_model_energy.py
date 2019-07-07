

from typing import List

import scipy

from core.kernel_generator.thermal_model import ThermalModel
from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, Task


class ThermalModelEnergy(ThermalModel):
    """
    Thermal model where task energy consumption is used to simulate the task heat generation
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

        tasks: List[Task] = tasks_specification.periodic_tasks + tasks_specification.aperiodic_tasks

        consumption_by_task = [task.e / (v_cpu * rho * cp) for task in tasks]

        return scipy.repeat(scipy.asarray(consumption_by_task).reshape((1, -1)), cpu_specification.number_of_cores,
                            axis=0)
