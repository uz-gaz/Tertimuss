import scipy
import scipy.integrate

from core.kernel_generator.global_model import GlobalModel
from core.tcpn_simulator.TcpnSimulatorAccurate import TcpnSimulatorAccurate


class GlobalModelSolver(object):
    def __init__(self, global_model: GlobalModel, step: float, n: int, m: int):
        self.__tcpn_simulator = TcpnSimulatorAccurate(global_model.pre, global_model.post, global_model.pi,
                                                      global_model.lambda_vector, step)
        self.__control = scipy.ones(len(global_model.lambda_vector))
        self.__mo = global_model.mo

        self.__n = n
        self.__m = m

    def run_step(self, w_alloc: scipy.ndarray) -> [scipy.ndarray, scipy.ndarray, scipy.ndarray,
                                                   scipy.ndarray, scipy.ndarray,
                                                   scipy.ndarray, scipy.ndarray]:
        new_control = scipy.copy(self.__control)
        new_control[self.__n:self.__n + len(w_alloc)] = w_alloc

        if not scipy.array_equal(self.__control, new_control):
            self.__control = new_control
            self.__tcpn_simulator.set_control(new_control)

        self.__mo = self.__tcpn_simulator.simulate_step(self.__mo)

        return scipy.concatenate([
            self.__mo[2 * self.__n + i * (2 * self.__n + 1):2 * self.__n + i * (2 * self.__n + 1) + self.__n,
            0].reshape(-1) for i in range(self.__m)])

    def get_mo(self):
        return self.__mo
