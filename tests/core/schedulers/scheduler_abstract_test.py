import hashlib
import unittest
import scipy.io

from main.core.problem_specification.cpu_specification.BoardSpecification import BoardSpecification
from main.core.problem_specification.cpu_specification.CoreGroupSpecification import CoreGroupSpecification
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.cpu_specification.EnergyConsumptionProperties import EnergyConsumptionProperties
from main.core.problem_specification.cpu_specification.MaterialCuboid import MaterialCuboid
from main.core.problem_specification.environment_specification.EnvironmentSpecification import EnvironmentSpecification
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.simulation_specification.TCPNModelSpecification import TCPNModelSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.problem_specification.tasks_specification.AperiodicTask import AperiodicTask
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.schedulers.templates.abstract_base_scheduler.AbstractBaseScheduler import AbstractBaseScheduler
from main.core.schedulers.templates.abstract_scheduler.SchedulerResult import SchedulerResult
from main.core.tcpn_model_generator.global_model import GlobalModel
from main.core.tcpn_model_generator.thermal_model_selector import ThermalModelSelector
from main.plot_generator.implementations.AccumulatedExecutionTimeDrawer import AccumulatedExecutionTimeDrawer
from main.plot_generator.implementations.EnergyConsumptionDrawer import EnergyConsumptionDrawer
from main.plot_generator.implementations.ExecutionPercentageDrawer import ExecutionPercentageDrawer
from main.plot_generator.implementations.FrequencyDrawer import FrequencyDrawer
from main.plot_generator.implementations.MaxCoreTemperatureDrawer import MaxCoreTemperatureDrawer
from main.plot_generator.implementations.TaskExecutionDrawer import TaskExecutionDrawer
from main.plot_generator.implementations.UtilizationDrawer import UtilizationDrawer


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
    def create_problem_specification(scheduler: AbstractBaseScheduler, is_thermal: bool,
                                     with_aperiodics: bool):
        tasks = [PeriodicTask(2000, 4, 4, 6.4), PeriodicTask(5000, 8, 8, 8), PeriodicTask(6000, 12, 12, 9.6)]

        if with_aperiodics:
            tasks.append(AperiodicTask(2000, 10, 20, 6))

        tasks_specification: TasksSpecification = TasksSpecification(tasks)

        core_specification = CoreGroupSpecification(MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                    EnergyConsumptionProperties(),
                                                    [150, 400, 600, 850, 1000],
                                                    [1000, 1000])

        board_specification = BoardSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400))

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01, is_thermal)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification,
                                                                        CpuSpecification(board_specification,
                                                                                         core_specification),
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification)

        return scheduler.simulate(global_specification, global_model, None), global_specification, global_model

    def run_test_hash_based(self, scheduler: AbstractBaseScheduler, is_thermal: bool,
                            with_aperiodics: bool, scheduler_assignation_hash: str):
        result, _, _ = self.create_problem_specification(scheduler, is_thermal, with_aperiodics)
        self.assertEqual(hashlib.md5(result.scheduler_assignation).hexdigest(), scheduler_assignation_hash)

    def run_test_matlab_result_based(self, scheduler: AbstractBaseScheduler, is_thermal: bool,
                                     with_aperiodics: bool, result_save_path: str):
        result, _, _ = self.create_problem_specification(scheduler, is_thermal, with_aperiodics)
        result_correct = self.load_scheduler_result_from_matlab_format(result_save_path, is_thermal)

        self.assertEqual(hashlib.md5(result.scheduler_assignation).hexdigest(),
                         hashlib.md5(result_correct.scheduler_assignation).hexdigest())

    def save_matlab_result(self, scheduler: AbstractBaseScheduler, is_thermal: bool,
                           with_aperiodics: bool, result_save_path: str):
        result, _, _ = self.create_problem_specification(scheduler, is_thermal, with_aperiodics)
        self.save_scheduler_result_in_matlab_format(result, result_save_path, is_thermal)

    def save_plot_outputs_result(self, scheduler: AbstractBaseScheduler, is_thermal: bool,
                                 with_aperiodics: bool, result_save_path: str):
        result, global_specification, simulation_kernel = self.create_problem_specification(scheduler,
                                                                                            is_thermal,
                                                                                            with_aperiodics)

        UtilizationDrawer.plot(global_specification, result, {"save_path": result_save_path + "_cpu_utilization.png"})
        TaskExecutionDrawer.plot(global_specification, result, {"save_path": result_save_path + "_task_execution.png"})

        AccumulatedExecutionTimeDrawer.plot(global_specification, result,
                                            {"save_path": result_save_path + "_accumulated_execution_time.png"})

        FrequencyDrawer.plot(global_specification, result, {"save_path": result_save_path + "_frequency.png"})
        ExecutionPercentageDrawer.plot(global_specification, result,
                                       {"save_path": result_save_path + "_execution_percentage.png"})
        if is_thermal:
            EnergyConsumptionDrawer.plot(global_specification, result,
                                         {"save_path": result_save_path + "_energy_consumption.png"})
            MaxCoreTemperatureDrawer.plot(global_specification, result,
                                          {"save_path": result_save_path + "_cpu_temperature.png"})

            # TODO: Uncomment
            # draw_heat_matrix(global_specification, result, True, True, result_save_path + "_heat_matrix.mp4")
