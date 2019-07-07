import pickle
import unittest

from core.kernel_generator.thermal_model_selector import ThermalModelSelector
from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TCPNModelSpecification import TCPNModelSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, PeriodicTask
from output_generation.output_generator import plot_cpu_frequency, plot_task_execution_percentage, plot_cpu_utilization, \
    plot_task_execution, plot_cpu_temperature, plot_accumulated_execution_time


class MyTestCase(unittest.TestCase):
    def test_something(self):
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

        scheduler_result = None

        with open('scheduler_simulation_result.pkl', 'rb') as f:
            scheduler_result = pickle.load(f)

        # plot_cpu_utilization(global_specification, scheduler_result, "out/global_edf_a_thermal_cpu_utilization.png")
        # plot_task_execution(global_specification, scheduler_result, "out/global_edf_a_thermal_task_execution.png")
        # plot_cpu_temperature(global_specification, scheduler_result, "out/global_edf_a_thermal_cpu_temperature.png")
        # plot_accumulated_execution_time(global_specification, scheduler_result,
        #                                 "out/global_edf_a_thermal_accumulated.png")
        # plot_cpu_frequency(global_specification, scheduler_result, "out/global_edf_a_thermal_frequency.png")
        plot_task_execution_percentage(global_specification, scheduler_result, "out/global_edf_a_thermal_execution.png")


if __name__ == '__main__':
    unittest.main()
