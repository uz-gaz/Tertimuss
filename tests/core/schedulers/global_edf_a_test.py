import time
import unittest

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, PeriodicTask, AperiodicTask
from core.schedulers.implementations.global_edf_a import GlobalEDFAffinityScheduler
from output_generation.output_generator import plot_cpu_utilization, plot_task_execution, plot_cpu_temperature, \
    plot_accumulated_execution_time


class TestGlobalEdfScheduler(unittest.TestCase):

    def test_global_edf_a_thermal(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8, 8),
                                                                      PeriodicTask(3, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        scheduler = GlobalEDFAffinityScheduler()

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification)

        global_model = GlobalModel(global_specification, True)

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        # draw_heat_matrix(global_specification, simulation_kernel, scheduler_simulation, "global_edf_a_thermal_heat_matrix.mp4")
        plot_cpu_utilization(global_specification, scheduler_simulation, "global_edf_a_thermal_cpu_utilization.png")
        plot_task_execution(global_specification, scheduler_simulation, "global_edf_a_thermal_task_execution.png")
        plot_cpu_temperature(global_specification, scheduler_simulation, "global_edf_a_thermal_cpu_temperature.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation,
                                        "global_edf_a_thermal_accumulated.png")

    def test_global_edf_a_var_frequency_thermal(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8, 8),
                                                                      PeriodicTask(3, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 0.5], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        scheduler = GlobalEDFAffinityScheduler()

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification)

        global_model = GlobalModel(global_specification, True)

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        # draw_heat_matrix(global_specification, simulation_kernel, scheduler_simulation, "global_edf_a_var_frequency_heat_matrix.mp4")
        plot_cpu_utilization(global_specification, scheduler_simulation, "gedf_a_var_frequency_cpu_utilization.png")
        plot_task_execution(global_specification, scheduler_simulation, "gedf_a_var_frequency_task_execution.png")
        plot_cpu_temperature(global_specification, scheduler_simulation, "gedf_a_var_frequency_cpu_temperature.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation,
                                        "gedf_a_var_frequency_accumulated.png")

    def test_global_edf_a_aperiodic_thermal(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8, 8),
                                                                      PeriodicTask(3, 12, 12, 9.6),
                                                                      AperiodicTask(2, 10, 20, 6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        scheduler = GlobalEDFAffinityScheduler()

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification)

        global_model = GlobalModel(global_specification, True)

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        # draw_heat_matrix(global_specification, simulation_kernel, scheduler_simulation, "global_edf_a_aperiodic_thermal_heat_matrix.mp4")
        plot_cpu_utilization(global_specification, scheduler_simulation, "gedf_a_aperiodic_thermal_cpu_utilization.png")
        plot_task_execution(global_specification, scheduler_simulation, "gedf_a_aperiodic_thermal_task_execution.png")
        plot_cpu_temperature(global_specification, scheduler_simulation, "gedf_a_aperiodic_thermal_cpu_temperature.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation,
                                        "gedf_a_aperiodic_thermal_accumulated.png")

    def test_global_edf_a_no_thermal(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8, 8),
                                                                      PeriodicTask(3, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        scheduler = GlobalEDFAffinityScheduler()

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification)

        global_model = GlobalModel(global_specification, False)

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        plot_cpu_utilization(global_specification, scheduler_simulation, "gedf_a_no_thermal_cpu_utilization.png")
        plot_task_execution(global_specification, scheduler_simulation, "gedf_a_no_thermal_task_execution.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation, "gedf_a_no_thermal_accumulated.png")


if __name__ == '__main__':
    unittest.main()
