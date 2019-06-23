import scipy
import scipy.integrate

from core.kernel_generator.global_model import GlobalModel
from core.tcpn_simulator.TcpnSimulatorAccurateOptimizedTasks import TcpnSimulatorAccurateOptimizedTasks
from core.tcpn_simulator.TcpnSimulatorAccurateOptimizedThermal import TcpnSimulatorAccurateOptimizedThermal
from core.tcpn_simulator.TcpnSimulatorOptimizedTasksAndProcessors import TcpnSimulatorOptimizedTasksAndProcessors


class GlobalModelSolver(object):
    def __init__(self, global_model: GlobalModel, step: float, n: int, m: int):
        self.__fragmentation_of_step = 20

        self.__tcpn_simulator_proc = TcpnSimulatorOptimizedTasksAndProcessors(global_model.pre_proc_tau,
                                                                              global_model.post_proc_tau,
                                                                              global_model.pi_proc_tau,
                                                                              global_model.lambda_vector_proc_tau,
                                                                              step / self.__fragmentation_of_step)

        self.__control = scipy.ones(len(global_model.lambda_vector_proc_tau))
        self.__mo = global_model.mo_proc_tau
        self.__n = n
        self.__m = m

        self.__step = step

        self.enable_thermal_mode = global_model.enable_thermal_mode

        if global_model.enable_thermal_mode:
            self.__tcpn_simulator_thermal = TcpnSimulatorAccurateOptimizedThermal(global_model.pre_thermal,
                                                                                  global_model.post_thermal,
                                                                                  global_model.pi_thermal,
                                                                                  global_model.lambda_vector_thermal,
                                                                                  step / self.__fragmentation_of_step)

            self.__mo_thermal = global_model.mo_thermal
            self.__p_board = global_model.p_board
            self.__p_one_micro = global_model.p_one_micro

    def run_step(self, w_alloc: scipy.ndarray, time: float) -> [scipy.ndarray, scipy.ndarray, scipy.ndarray,
                                                                scipy.ndarray, scipy.ndarray,
                                                                scipy.ndarray, scipy.ndarray]:

        new_control = scipy.copy(self.__control)
        new_control[self.__n:self.__n + len(w_alloc)] = w_alloc

        if not scipy.array_equal(self.__control, new_control):
            self.__control = new_control
            self.__tcpn_simulator_proc.set_control(new_control)

        partial_results_proc = []
        for _ in range(self.__fragmentation_of_step):
            self.__mo = self.__tcpn_simulator_proc.simulate_step(self.__mo)
            partial_results_proc.append(self.__mo)

        board_temperature = None
        cores_temperature = None

        if self.enable_thermal_mode:
            # partial_results_thermal = []
            for mo_actual in partial_results_proc:
                m_exec = scipy.concatenate([mo_actual[2 * self.__n + (2 * self.__n + 1) * i:2 * self.__n + (
                        2 * self.__n + 1) * i + self.__n, 0] for i in range(self.__m)])

                m_exec = m_exec * (1 / self.__step)  # FIXME: Review it

                self.__mo_thermal[-self.__n * self.__m:, 0] = m_exec
                self.__mo_thermal = self.__tcpn_simulator_thermal.simulate_step(self.__mo_thermal)
                # partial_results_thermal.append(self.__mo_thermal)

                board_temperature = self.__mo_thermal[0:self.__p_board + self.__p_one_micro * self.__m, 0]

                cores_temperature = [
                    self.__mo_thermal[self.__p_board + i * self.__p_one_micro + int(self.__p_one_micro / 2), 0]
                    for i in range(self.__m)]  # Take the temperature in the center of the core

                cores_temperature = scipy.asarray(cores_temperature).reshape((-1, 1))

            board_temperature = board_temperature.reshape((-1, 1))

        return scipy.concatenate([
            self.__mo[
            2 * self.__n + i * (2 * self.__n + 1) + self.__n:2 * self.__n + i * (2 * self.__n + 1) + 2 * self.__n,
            0].reshape(-1) for i in range(self.__m)]), board_temperature, cores_temperature, scipy.asarray(
            [time + self.__step])

    def get_mo(self):
        return self.__mo
