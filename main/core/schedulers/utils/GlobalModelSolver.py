from typing import List

import scipy
import scipy.integrate

from main.core.tcpn_model_generator.GlobalModel import GlobalModel
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.tcpn_simulator.implementation.numerical_integration.TcpnSimulatorOptimizedTasksAndProcessors import \
    TcpnSimulatorOptimizedTasksAndProcessors
from main.core.tcpn_simulator.implementation.numerical_integration.TcpnSimulatorOptimizedThermal import \
    TcpnSimulatorAccurateOptimizedThermal


class GlobalModelSolver(object):
    def __init__(self, global_model: GlobalModel, global_specification: GlobalSpecification):
        """

        :param global_model: Global model
        :param global_specification: Global specification
        """

        self.__n = len(global_specification.tasks_specification.periodic_tasks) + \
                   len(global_specification.tasks_specification.aperiodic_tasks)
        self.__m = len(global_specification.cpu_specification.cores_specification.cores_frequencies)
        self.__step = global_specification.simulation_specification.dt
        self.enable_thermal_mode = global_model.enable_thermal_mode

        self.__fragmentation_of_step_task = \
            global_specification.simulation_specification.dt_fragmentation_processor_task
        self.__fragmentation_of_step_thermal = global_specification.simulation_specification.dt_fragmentation_thermal

        self.__tcpn_simulator_proc = TcpnSimulatorOptimizedTasksAndProcessors(global_model.pre_proc_tau,
                                                                              global_model.post_proc_tau,
                                                                              global_model.pi_proc_tau,
                                                                              global_model.lambda_vector_proc_tau,
                                                                              self.__fragmentation_of_step_task,
                                                                              self.__step)

        self.__control_task_proc = scipy.ones(len(global_model.lambda_vector_proc_tau))
        self.__mo = global_model.mo_proc_tau

        # M exec of the previous step
        self.__last_tcpn_m_exec = scipy.zeros(self.__n * self.__m)

        # Real accumulated execution time
        self.__accumulated_m_exec = scipy.zeros(self.__n * self.__m)

        # T_alloc start index
        self.__t_alloc_start_index = len(global_specification.tasks_specification.periodic_tasks)

        # Processor model places start index
        self.__m_processor_start_index = 2 * len(global_specification.tasks_specification.periodic_tasks) + len(
            global_specification.tasks_specification.aperiodic_tasks)

        # Selected thermal model
        self.__thermal_model_selected = global_specification.tcpn_model_specification.thermal_model_selector

        # Model specification
        self.__cpu_specification = global_specification.cpu_specification
        self.__tasks_specification = global_specification.tasks_specification
        self.__simulation_specification = global_specification.simulation_specification

        if global_model.enable_thermal_mode:
            self.__tcpn_simulator_thermal = TcpnSimulatorAccurateOptimizedThermal(global_model.pre_thermal,
                                                                                  global_model.post_thermal,
                                                                                  global_model.pi_thermal,
                                                                                  global_model.lambda_vector_thermal,
                                                                                  self.__step / self.__fragmentation_of_step_thermal,
                                                                                  self.__fragmentation_of_step_thermal)

            self.__mo_thermal = global_model.mo_thermal
            self.__p_board = global_model.p_board
            self.__p_one_micro = global_model.p_one_micro

            base_frequency = global_specification.cpu_specification.cores_specification.available_frequencies[-1]
            clock_relative_frequencies = [i / base_frequency for i in
                                          global_specification.cpu_specification.cores_specification.available_frequencies]

            self.__control_thermal = scipy.asarray(clock_relative_frequencies)
            self.__power_consumption = global_model.power_consumption

    def run_step(self, w_alloc: List[int], core_frequencies: List[float]) -> [scipy.ndarray,
                                                                              scipy.ndarray,
                                                                              scipy.ndarray,
                                                                              scipy.ndarray,
                                                                              scipy.ndarray,
                                                                              scipy.ndarray,
                                                                              scipy.ndarray]:
        """
        Run one simulation step
        :param w_alloc: allocation vector
        :param core_frequencies: actual relative cores frequency
        :return execution time after simulation, board temperature after simulation, cores max temperature after
                simulation, time of temperatures measurements
        """

        # Transform core frequencies to control action over t_alloc and t_exec
        core_frequencies_as_control = [self.__n * [i] for i in core_frequencies]
        core_frequencies_as_control = scipy.concatenate(core_frequencies_as_control)

        # Create new control vector
        new_control_processor = scipy.copy(self.__control_task_proc)
        # Control over t_alloc
        new_control_processor[self.__t_alloc_start_index:self.__t_alloc_start_index + self.__n * self.__m] = \
            scipy.asarray(w_alloc) * core_frequencies_as_control
        # Control over t_exec
        new_control_processor[-self.__n * self.__m:] = core_frequencies_as_control

        if not scipy.array_equal(self.__control_task_proc, new_control_processor):
            self.__control_task_proc = new_control_processor
            self.__tcpn_simulator_proc.set_control(new_control_processor)

        self.__mo = self.__tcpn_simulator_proc.simulate_step(self.__mo)

        board_temperature = None
        cores_temperature = None

        if self.enable_thermal_mode:
            # Create new control vector
            new_control_thermal = scipy.asarray(core_frequencies)

            if not scipy.array_equal(self.__control_thermal, new_control_thermal):
                self.__control_thermal = new_control_thermal

                # Obtain post and lambda for the new frequency
                post, lambda_vector, power_consumption = \
                    self.__thermal_model_selected.value.change_frequency(core_frequencies,
                                                                         self.__tcpn_simulator_thermal.get_post(),
                                                                         self.__tcpn_simulator_thermal.get_lambda(),
                                                                         self.__cpu_specification,
                                                                         self.__tasks_specification,
                                                                         self.__p_board,
                                                                         self.__p_one_micro,
                                                                         self.__simulation_specification)

                self.__tcpn_simulator_thermal.set_post_and_lambda(post, lambda_vector)
                self.__power_consumption = power_consumption

            self.__mo_thermal[-self.__n * self.__m:, 0] = w_alloc
            self.__mo_thermal = self.__tcpn_simulator_thermal.simulate_multi_step(self.__mo_thermal)

            board_temperature = self.__mo_thermal[0:self.__p_board + self.__p_one_micro * self.__m, 0]
            board_temperature = board_temperature.reshape((-1, 1))

            cores_temperature = [
                self.__mo_thermal[self.__p_board + i * self.__p_one_micro + int(self.__p_one_micro / 2), 0]
                for i in range(self.__m)]  # Take the temperature in the center of the core

            cores_temperature = scipy.asarray(cores_temperature).reshape((-1, 1))

        # As the m_exec computed by the tcpn is relative to the cycles executed, we need to transform it to a time
        # measurement

        m_exec_this_step = scipy.concatenate([
            self.__mo[
            self.__m_processor_start_index + i * (2 * self.__n + 1) +
            self.__n:self.__m_processor_start_index + i * (
                    2 * self.__n + 1) + 2 * self.__n, 0].reshape(-1) for i in range(self.__m)])

        m_exec_change = (m_exec_this_step - self.__last_tcpn_m_exec) / core_frequencies_as_control

        self.__last_tcpn_m_exec = m_exec_this_step

        self.__accumulated_m_exec += m_exec_change

        # Obtain energy consumption
        energy_consumption = None
        if self.enable_thermal_mode:
            energy_consumption = scipy.sum(
                scipy.asarray(w_alloc).reshape(self.__m, self.__n) * self.__power_consumption,
                axis=1)

        return self.__accumulated_m_exec, board_temperature, cores_temperature, energy_consumption

    def get_mo(self):
        return self.__mo
