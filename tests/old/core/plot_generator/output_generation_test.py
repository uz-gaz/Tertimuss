import os
import unittest

import scipy.io

from main.core.execution_simulator.system_modeling.ThermalModelSelector import ThermalModelSelector
from main.core.execution_simulator.system_simulator.SchedulingResult import SchedulingResult
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.cpu_specification.BoardSpecification import BoardSpecification
from main.core.problem_specification.cpu_specification.CoreGroupSpecification import CoreGroupSpecification
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.cpu_specification.EnergyConsumptionProperties import EnergyConsumptionProperties
from main.core.problem_specification.cpu_specification.MaterialCuboid import MaterialCuboid
from main.core.problem_specification.environment_specification.EnvironmentSpecification import EnvironmentSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.simulation_specification.TCPNModelSpecification import TCPNModelSpecification
from main.core.problem_specification.tasks_specification.AperiodicTask import AperiodicTask
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.plot_generator.implementations.ContextSwitchStatistics import ContextSwitchStatistics
from main.plot_generator.implementations.ExecutionPercentageStatistics import ExecutionPercentageStatistics
from main.plot_generator.implementations.TaskExecutionDrawer import TaskExecutionDrawer
from main.plot_generator.implementations.UtilizationDrawer import UtilizationDrawer


class OutputGenerationTest(unittest.TestCase):
    @staticmethod
    def __load_scheduler_result_from_matlab_format(path: str, is_thermal: bool) -> SchedulingResult:
        matlab_file = scipy.io.loadmat(path + ".mat")
        time_steps = matlab_file["time_steps"][0]
        temperature_map = matlab_file["temperature_map"] if is_thermal else None
        max_temperature_cores = matlab_file["max_temperature_cores"] if is_thermal else None
        execution_time_scheduler = matlab_file["execution_time_scheduler"]
        execution_time_tcpn = matlab_file["execution_time_tcpn"]
        frequencies = matlab_file["frequencies"]
        energy_consumption = matlab_file["energy_consumption"] if is_thermal else None
        scheduler_assignation = matlab_file["scheduler_assignation"]
        quantum = matlab_file["time_steps"][0][0]
        return SchedulingResult(temperature_map, max_temperature_cores, time_steps, execution_time_scheduler,
                                execution_time_tcpn, scheduler_assignation, frequencies, energy_consumption, quantum)

    @staticmethod
    def __create_problem_specification(is_thermal: bool, with_aperiodics: bool) -> GlobalSpecification:
        tasks = [PeriodicTask(2000000, 4, 4, 3.4), PeriodicTask(5000000, 8, 8, 8), PeriodicTask(6000000, 12, 12, 9.6)]

        if with_aperiodics:
            tasks.append(AperiodicTask(2000000, 10, 20, 6))

        tasks_specification: TasksSpecification = TasksSpecification(tasks)

        core_specification = CoreGroupSpecification(MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                    EnergyConsumptionProperties(),
                                                    [150000, 400000, 600000, 850000, 1000000],
                                                    [1000000, 1000000])

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

        return global_specification

    @classmethod
    def __global_config(cls):
        # Path of the input validate schema
        input_schema_path = './input/g_edf_a_thermal'
        absolute_input_schema_path = os.path.join(os.path.dirname(__file__), input_schema_path)

        result = cls.__load_scheduler_result_from_matlab_format(absolute_input_schema_path, True)
        global_specification = cls.__create_problem_specification(True, False)

        output_path = './out/g_edf_a_thermal'

        return result, global_specification, output_path

    def test_execution_percentage_statics(self):
        result_to_plot, global_specification, output_path = self.__global_config()
        ExecutionPercentageStatistics.plot(global_specification, result_to_plot,
                                           {"save_path": output_path + "_execution_percentage_statics.json"})

    def test_context_switch_statics(self):
        result_to_plot, global_specification, output_path = self.__global_config()
        ContextSwitchStatistics.plot(global_specification, result_to_plot,
                                     {"save_path": output_path + "_context_switch_statics.json"})

    def test_utilization(self):
        result_to_plot, global_specification, output_path = self.__global_config()
        UtilizationDrawer.plot(global_specification, result_to_plot,
                               {"save_path": output_path + "_utilization.png"})

    def test_tasks_execution(self):
        result_to_plot, global_specification, output_path = self.__global_config()
        TaskExecutionDrawer.plot(global_specification, result_to_plot,
                                 {"save_path": output_path + "_tasks_execution.png"})


if __name__ == '__main__':
    unittest.main()
