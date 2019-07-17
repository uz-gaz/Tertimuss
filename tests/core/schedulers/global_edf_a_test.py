import time
import unittest

from core.tcpn_model_generator.global_model import GlobalModel
from core.tcpn_model_generator.thermal_model_selector import ThermalModelSelector
from core.problem_specification.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification.GlobalSpecification import GlobalSpecification
from core.problem_specification.SimulationSpecification import SimulationSpecification
from core.problem_specification.TCPNModelSpecification import TCPNModelSpecification
from core.problem_specification.TasksSpecification import TasksSpecification, PeriodicTask, AperiodicTask
from core.schedulers.implementations.global_edf_a import GlobalEDFAffinityScheduler
from plot_generator.output_generator import plot_cpu_utilization, plot_task_execution, plot_cpu_temperature, \
    plot_accumulated_execution_time, plot_task_execution_percentage, plot_cpu_frequency, draw_heat_matrix, \
    plot_energy_consumption
import scipy.io


class TestGlobalEdfScheduler(unittest.TestCase):

    def test_global_edf_a_thermal(self):
        time_1 = time.time()
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(5, 8, 8, 8),
                                                                      PeriodicTask(6, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)
        scheduler = GlobalEDFAffinityScheduler()

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification, True)

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        print("Time taken in simulation:", time.time() - time_1)

        time_1 = time.time()

        # Result base name
        result_base_name = "global_edf_a_thermal"

        # Save simulation out
        scipy.io.savemat("out/" + result_base_name + ".mat", {
            'frequencies': scheduler_simulation.frequencies,
            'scheduler_assignation': scheduler_simulation.scheduler_assignation,
            'time_scheduler': scheduler_simulation.time_steps,
            'temperature_map': scheduler_simulation.temperature_map,
            'max_temperature_cores': scheduler_simulation.max_temperature_cores,
            'execution_time_scheduler': scheduler_simulation.execution_time_scheduler
        })

        print("Time taken in matlab file save:", time.time() - time_1)

        time_1 = time.time()

        # Save plots
        # draw_heat_matrix(global_specification, scheduler_simulation, True, True,
        #                  "out/" + result_base_name + "_heat_matrix.mp4")

        plot_cpu_utilization(global_specification, scheduler_simulation,
                             "out/" + result_base_name + "_cpu_utilization.png")
        plot_task_execution(global_specification, scheduler_simulation,
                            "out/" + result_base_name + "_task_execution.png")
        plot_cpu_temperature(global_specification, scheduler_simulation,
                             "out/" + result_base_name + "_cpu_max_temperature.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation,
                                        "out/" + result_base_name + "_accumulated.png")
        plot_cpu_frequency(global_specification, scheduler_simulation, "out/" + result_base_name + "_frequency.png")
        plot_task_execution_percentage(global_specification, scheduler_simulation,
                                       "out/" + result_base_name + "_execution_percentage.png")

        plot_energy_consumption(global_specification, scheduler_simulation,
                                "out/" + result_base_name + "_energy_consumption.png")

        print("Time taken in save output:", time.time() - time_1)

        """
        Step 2:
        Time taken in simulation: 2.13 s
        Time taken in matlab file save: 0.06 s
        Time taken in save output: 198.74 s -> 3 min 19 S
        
        Step 1:
        Time taken in simulation: 35.89 s
        Time taken in matlab file save: 0.28 s
        Time taken in save output: 211.06 s -> 3 min 31 s
        
        Steo 0.5:
        Time taken in simulation: 1026.83 s -> 17 min 6s
        Time taken in matlab file save: 1.34 s
        Time taken in save output: 240.32 s -> 4 min
        """

    def test_global_edf_a_var_frequency_thermal(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(5, 8, 8, 8),
                                                                      PeriodicTask(6, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 0.5], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_ENERGY_BASED)

        scheduler = GlobalEDFAffinityScheduler()

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification, True)

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        # draw_heat_matrix(global_specification, simulation_kernel, scheduler_simulation, "global_edf_a_var_frequency_heat_matrix.mp4")
        # plot_cpu_utilization(global_specification, scheduler_simulation, "out/gedf_a_var_frequency_cpu_utilization.png")
        # plot_task_execution(global_specification, scheduler_simulation, "out/gedf_a_var_frequency_task_execution.png")
        plot_cpu_temperature(global_specification, scheduler_simulation,
                             "out/gedf_a_var_frequency_cpu_temperature.png")
        # plot_accumulated_execution_time(global_specification, scheduler_simulation,
        #                                 "out/gedf_a_var_frequency_accumulated.png")
        # plot_cpu_frequency(global_specification, scheduler_simulation, "out/gedf_a_var_frequency_frequency.png")
        # plot_task_execution_percentage(global_specification, scheduler_simulation,
        #                                "out/gedf_a_var_frequency_execution_percentage.png")

    def test_global_edf_a_aperiodic_thermal(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(5, 8, 8, 8),
                                                                      PeriodicTask(6, 12, 12, 9.6),
                                                                      AperiodicTask(2, 10, 20, 6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

        scheduler = GlobalEDFAffinityScheduler()

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification, True)

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        # Result base name
        result_base_name = "global_edf_a_thermal_aperiodics"

        # Save plots
        # draw_heat_matrix(global_specification, scheduler_simulation, True, True,
        #                  "out/" + result_base_name + "_heat_matrix.mp4")

        plot_cpu_utilization(global_specification, scheduler_simulation,
                             "out/" + result_base_name + "_cpu_utilization.png")
        plot_task_execution(global_specification, scheduler_simulation,
                            "out/" + result_base_name + "_task_execution.png")
        plot_cpu_temperature(global_specification, scheduler_simulation,
                             "out/" + result_base_name + "_cpu_max_temperature.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation,
                                        "out/" + result_base_name + "_accumulated.png")
        plot_cpu_frequency(global_specification, scheduler_simulation, "out/" + result_base_name + "_frequency.png")
        plot_task_execution_percentage(global_specification, scheduler_simulation,
                                       "out/" + result_base_name + "_execution_percentage.png")

        plot_energy_consumption(global_specification, scheduler_simulation,
                                "out/" + result_base_name + "_energy_consumption.png")

    def test_global_edf_a_no_thermal(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(5, 8, 8, 8),
                                                                      PeriodicTask(6, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

        scheduler = GlobalEDFAffinityScheduler()

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification, False)

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        plot_cpu_utilization(global_specification, scheduler_simulation, "out/gedf_a_no_thermal_cpu_utilization.png")
        plot_task_execution(global_specification, scheduler_simulation, "out/gedf_a_no_thermal_task_execution.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation,
                                        "out/gedf_a_no_thermal_accumulated.png")
        plot_cpu_frequency(global_specification, scheduler_simulation, "out/gedf_a_no_thermal_frequency.png")
        plot_task_execution_percentage(global_specification, scheduler_simulation,
                                       "out/gedf_a_no_thermal_execution_percentage.png")


if __name__ == '__main__':
    unittest.main()
