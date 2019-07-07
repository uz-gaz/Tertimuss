import unittest

from core.kernel_generator.global_model import GlobalModel
from core.kernel_generator.thermal_model_selector import ThermalModelSelector
from core.problem_specification_models.CpuSpecification import MaterialCuboid, CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TCPNModelSpecification import TCPNModelSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, PeriodicTask, AperiodicTask
from core.schedulers.implementations.global_jdeds import GlobalJDEDSScheduler
from output_generation.output_generator import plot_cpu_utilization, plot_task_execution, plot_cpu_temperature, \
    plot_accumulated_execution_time, plot_cpu_frequency, plot_task_execution_percentage


class GlobalWodes(unittest.TestCase):
    def test_lpp(self):
        ci = [9, 9, 8]
        ti = [10, 10, 40]
        s, sd, hyperperiod, isd = GlobalJDEDSScheduler.ilpp_dp(ci, ti, 3, 2)

    def test_lpp_2(self):
        ci = [2000, 5000, 6000, 1800]
        ti = [3400, 6800, 10200, 20400]
        s, sd, hyperperiod, isd = GlobalJDEDSScheduler.ilpp_dp(ci, ti, 4, 2)

    def test_scheduler_with_thermal(self):
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

        scheduler = GlobalJDEDSScheduler()

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification, True)

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        # draw_heat_matrix(global_specification, simulation_kernel, scheduler_simulation, "affinity_heat_matrix.mp4")
        plot_cpu_utilization(global_specification, scheduler_simulation, "out/jdeds_cpu_utilization_thermal.png")
        plot_task_execution(global_specification, scheduler_simulation, "out/jdeds_task_execution_thermal.png")
        plot_cpu_temperature(global_specification, scheduler_simulation, "out/jdeds_cpu_temperature_thermal.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation, "out/jdeds_accumulated_thermal.png")
        plot_cpu_frequency(global_specification, scheduler_simulation,
                           "out/jdeds_frequency.png")
        plot_task_execution_percentage(global_specification, scheduler_simulation,
                                       "out/jdeds_execution_percentage.png")

    def test_scheduler_no_thermal(self):
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

        scheduler = GlobalJDEDSScheduler()

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification, False)

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        plot_cpu_utilization(global_specification, scheduler_simulation, "out/jdeds_no_thermal__cpu_utilization.png")
        plot_task_execution(global_specification, scheduler_simulation, "out/jdeds_no_thermal__task_execution.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation,
                                        "out/jdeds_no_thermal__accumulated.png")
        plot_cpu_frequency(global_specification, scheduler_simulation,
                           "out/jdeds_no_thermal_frequency.png")
        plot_task_execution_percentage(global_specification, scheduler_simulation,
                                       "out/jdeds_no_thermal__execution_percentage.png")


if __name__ == '__main__':
    unittest.main()
