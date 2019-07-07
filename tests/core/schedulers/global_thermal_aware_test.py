import unittest

from core.kernel_generator.global_model import GlobalModel
from core.kernel_generator.thermal_model_selector import ThermalModelSelector
from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TCPNModelSpecification import TCPNModelSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, PeriodicTask
from core.schedulers.implementations.global_thermal_aware import GlobalThermalAwareScheduler
from output_generation.output_generator import plot_cpu_utilization, plot_task_execution, plot_cpu_temperature, \
    plot_accumulated_execution_time


class RtTcpnScheduler(unittest.TestCase):

    def test_global_thermal_aware_scheduler_thermal(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(5, 8, 8, 8),
                                                                      PeriodicTask(6, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_ENERGY_BASED)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification, True)

        scheduler = GlobalThermalAwareScheduler()

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        # draw_heat_matrix(global_specification, simulation_kernel, scheduler_simulation, "global_thermal_aware_heat_matrix.mp4")
        plot_cpu_utilization(global_specification, scheduler_simulation, "out/global_thermal_aware_cpu_utilization.png")
        plot_task_execution(global_specification, scheduler_simulation, "out/global_thermal_aware_task_execution.png")
        plot_cpu_temperature(global_specification, scheduler_simulation, "out/global_thermal_aware_cpu_temperature.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation,
                                        "out/global_thermal_aware_accumulated.png")

    def test_global_thermal_aware_scheduler_no_thermal(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(5, 8, 8, 8),
                                                                      PeriodicTask(6, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_ENERGY_BASED)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification, tcpn_model_specification)

        global_model = GlobalModel(global_specification, True)

        scheduler = GlobalThermalAwareScheduler()

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        # draw_heat_matrix(global_specification, simulation_kernel, scheduler_simulation, "global_thermal_aware_no_thermal_heat_matrix.mp4")
        plot_cpu_utilization(global_specification, scheduler_simulation,
                             "out/global_thermal_aware_no_thermal_cpu_utilization.png")
        plot_task_execution(global_specification, scheduler_simulation,
                            "out/global_thermal_aware_no_thermal_task_execution.png")
        plot_cpu_temperature(global_specification, scheduler_simulation, "out/global_thermal_aware_cpu_temperature.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation,
                                        "out/global_thermal_aware_no_thermal_accumulated.png")


if __name__ == '__main__':
    unittest.main()
