import scipy
import scipy.integrate

from core.kernel_generator.global_model import GlobalModel


def solve_global_model_old(global_model: GlobalModel, mo: scipy.ndarray, w_alloc: scipy.ndarray, ma: float,
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
    a = global_model.a
    b = global_model.b
    d = global_model.bp
    c = global_model.s
    u = w_alloc

    t0 = time_sol[0]
    t1 = time_sol[1]

    step = (t1 - t0) / 10

    tout = scipy.arange(t0, t1, step)

    x = scipy.zeros((len(mo), len(tout)))

    x[:, 0] = mo

    aux_2 = b.dot(u.reshape((-1, 1))) + d * ma

    for j in range(1, len(tout)):
        x[:, j] = (a.dot(x[:, j - 1].reshape((-1, 1))) + aux_2).reshape(-1) * step + x[:, j - 1]

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
    a = global_model.a
    b = global_model.b
    d = global_model.bp
    c = global_model.s
    u = w_alloc

    t0 = time_sol[0]
    t1 = time_sol[1]

    step = (t1 - t0) / 10

    tout = scipy.arange(t0, t1, step)

    x = scipy.zeros((len(mo), len(tout)))

    x[:, 0] = mo

    aux_2 = b.dot(u.reshape((-1, 1))) + d * ma

    for j in range(1, len(tout)):
        x[:, j] = (a.dot(x[:, j - 1].reshape((-1, 1))) + aux_2).reshape(-1) * step + x[:, j - 1]

    m_m = (x.transpose()[- 1]).reshape((-1, 1))

    y_m = global_model.s.dot(m_m)

    temp_time = global_model.s.dot(x)[2 * len(w_alloc): len(y_m), :]

    m_busy = y_m[0:len(w_alloc)]
    m_exec = y_m[len(w_alloc): 2 * len(w_alloc)]
    temp = y_m[2 * len(w_alloc): len(y_m)]

    return m_m, m_exec.reshape((-1, 1)), m_busy.reshape((-1, 1)), temp.reshape(
        (-1, 1)), tout.reshape((-1, 1)), temp_time, x
