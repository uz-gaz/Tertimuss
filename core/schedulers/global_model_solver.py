import scipy
import scipy.integrate

from core.kernel_generator.global_model import GlobalModel


def solve_global_model(global_model: GlobalModel, mo: scipy.ndarray, w_alloc: scipy.ndarray, ma: float,
                       time_sol: list) -> [scipy.ndarray, scipy.ndarray, scipy.ndarray,
                                                    scipy.ndarray, scipy.ndarray,
                                                    scipy.ndarray, scipy.ndarray]:
    """
    Solve global model and obtain the next state in the TCPN
    :param global_model: global model
    :param mo: initial marking
    :param w_alloc:
    :param ma:
    :param time_sol: interval where solve the model
    :return:
    """
    aux = global_model.b.dot(w_alloc) + global_model.bp.reshape(-1) * ma
    res = scipy.integrate.solve_ivp(lambda t, m: global_model.a.dot(m.transpose()) + aux, time_sol, mo,
                                    dense_output=True)
    m_m = res.y.transpose()[- 1]

    y_m = global_model.s.dot(m_m)

    temp_time = global_model.s.dot(res.y)[2 * len(w_alloc): len(y_m), :]

    m_busy = y_m[0:len(w_alloc)]
    m_exec = y_m[len(w_alloc): 2 * len(w_alloc)]
    temp = y_m[2 * len(w_alloc): len(y_m)]

    return m_m.reshape((-1, 1)), m_exec.reshape((-1, 1)), m_busy.reshape((-1, 1)), temp.reshape(
        (-1, 1)), res.t.reshape((-1, 1)), temp_time, res.y
