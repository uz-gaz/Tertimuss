import hashlib
import unittest
import scipy.io

from core.problem_specification.CpuSpecification import MaterialCuboid, CpuSpecification
from core.problem_specification.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification.GlobalSpecification import GlobalSpecification
from core.problem_specification.SimulationSpecification import SimulationSpecification
from core.problem_specification.TCPNModelSpecification import TCPNModelSpecification
from core.problem_specification.TasksSpecification import TasksSpecification, PeriodicTask, AperiodicTask
from core.schedulers.templates.abstract_global_scheduler import AbstractGlobalScheduler
from core.schedulers.templates.abstract_scheduler import SchedulerResult
from core.tcpn_model_generator.global_model import GlobalModel
from core.tcpn_model_generator.thermal_model_selector import ThermalModelSelector
from plot_generator.output_generator import plot_cpu_utilization, plot_task_execution, plot_cpu_temperature, \
    plot_accumulated_execution_time, plot_task_execution_percentage, plot_cpu_frequency, draw_heat_matrix, \
    plot_energy_consumption


class SchedulerAbstractTest(unittest.TestCase):
    @staticmethod
    def load_scheduler_result_from_matlab_format(path: str, is_thermal: bool) -> SchedulerResult:
        matlab_file = scipy.io.loadmat(path + ".mat")
        time_steps = matlab_file["time_steps"][0]
        temperature_map = matlab_file["temperature_map"] if is_thermal else None
        max_temperature_cores = matlab_file["max_temperature_cores"] if is_thermal else None
        execution_time_scheduler = matlab_file["execution_time_scheduler"]
        frequencies = matlab_file["frequencies"]
        energy_consumption = matlab_file["energy_consumption"] if is_thermal else None
        scheduler_assignation = matlab_file["scheduler_assignation"]
        quantum = matlab_file["time_steps"][0][0]
        return SchedulerResult(temperature_map, max_temperature_cores, time_steps, execution_time_scheduler,
                               scheduler_assignation, frequencies, energy_consumption,
                               quantum)

    @staticmethod
    def save_scheduler_result_in_matlab_format(scheduler_simulation: SchedulerResult, path: str, is_thermal: bool):
        if is_thermal:
            scipy.io.savemat(path + ".mat", {
                'time_steps': scheduler_simulation.time_steps,
                'temperature_map': scheduler_simulation.temperature_map,
                'max_temperature_cores': scheduler_simulation.max_temperature_cores,
                'execution_time_scheduler': scheduler_simulation.execution_time_scheduler,
                'frequencies': scheduler_simulation.frequencies,
                'energy_consumption': scheduler_simulation.energy_consumption,
                'scheduler_assignation': scheduler_simulation.scheduler_assignation,
                'quantum': scheduler_simulation.quantum
            })
        else:
            scipy.io.savemat(path + ".mat", {
                'time_steps': scheduler_simulation.time_steps,
                'execution_time_scheduler': scheduler_simulation.execution_time_scheduler,
                'frequencies': scheduler_simulation.frequencies,
                'scheduler_assignation': scheduler_simulation.scheduler_assignation,
                'quantum': scheduler_simulation.quantum
            })

    @staticmethod
    def create_problem_specification(scheduler: AbstractGlobalScheduler, is_thermal: bool,
                                     with_aperiodics: bool):
        tasks = [PeriodicTask(2, 4, 4, 6.4), PeriodicTask(5, 8, 8, 8), PeriodicTask(6, 12, 12, 9.6)]

        if with_aperiodics:
            tasks.append(AperiodicTask(2, 10, 20, 6))

        tasks_specification: TasksSpecification = TasksSpecification(tasks)

        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification, is_thermal)

        return scheduler.simulate(global_specification, global_model, None), global_specification, global_model

    def run_test_hash_based(self, scheduler: AbstractGlobalScheduler, is_thermal: bool,
                            with_aperiodics: bool, scheduler_assignation_hash: str):
        result, _, _ = self.create_problem_specification(scheduler, is_thermal, with_aperiodics)
        self.assertEqual(hashlib.md5(result.scheduler_assignation).hexdigest(), scheduler_assignation_hash)

    def run_test_matlab_result_based(self, scheduler: AbstractGlobalScheduler, is_thermal: bool,
                                     with_aperiodics: bool, result_save_path: str):
        result, _, _ = self.create_problem_specification(scheduler, is_thermal, with_aperiodics)
        result_correct = self.load_scheduler_result_from_matlab_format(result_save_path, is_thermal)

        self.assertEqual(hashlib.md5(result.scheduler_assignation).hexdigest(),
                         hashlib.md5(result_correct.scheduler_assignation).hexdigest())

    def save_matlab_result(self, scheduler: AbstractGlobalScheduler, is_thermal: bool,
                           with_aperiodics: bool, result_save_path: str):
        result, _, _ = self.create_problem_specification(scheduler, is_thermal, with_aperiodics)
        self.save_scheduler_result_in_matlab_format(result, result_save_path, is_thermal)

    def save_plot_outputs_result(self, scheduler: AbstractGlobalScheduler, is_thermal: bool,
                                 with_aperiodics: bool, result_save_path: str):
        result, global_specification, simulation_kernel = self.create_problem_specification(scheduler,
                                                                                            is_thermal,
                                                                                            with_aperiodics)

        # TODO: Uncomment
        # draw_heat_matrix(global_specification, result, True, True, result_save_path + "_heat_matrix.mp4")
        plot_cpu_utilization(global_specification, result, result_save_path + "_cpu_utilization.png")
        plot_task_execution(global_specification, result, result_save_path + "_task_execution.png")

        plot_accumulated_execution_time(global_specification, result,
                                        result_save_path + "_accumulated_execution_time.png")
        plot_cpu_frequency(global_specification, result, result_save_path + "_frequency.png")
        plot_task_execution_percentage(global_specification, result,
                                       result_save_path + "_execution_percentage.png")
        if is_thermal:
            plot_energy_consumption(global_specification, result,
                                    result_save_path + "_energy_consumption.png")
            plot_cpu_temperature(global_specification, result, result_save_path + "_cpu_temperature.png")
