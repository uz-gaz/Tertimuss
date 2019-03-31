import numpy as np
import scipy.integrate

from core.kernel_generator.global_model import GlobalModel


def solve_global_model(global_model: GlobalModel, mo: np.ndarray, w_alloc: np.ndarray, ma: float,
                       time_sol: np.ndarray) -> [np.ndarray, np.ndarray, np.ndarray,
                                                 np.ndarray, np.ndarray,
                                                 np.ndarray, np.ndarray]:
    res = scipy.integrate.solve_ivp(
        lambda t, m: GLOBAL(m, global_model.a, global_model.b, global_model.bp, w_alloc, ma), time_sol, mo
    )  # Review final dimensions

    m_aux = res.y.transpose()

    m_aux = m_aux[len(m_aux) - 1]

    y_m = global_model.s.dot(m_aux)

    t_aux = global_model.s.dot(res.y)

    temp_time = t_aux[2 * len(w_alloc): len(y_m), :]

    m_busy = y_m[0:len(w_alloc)]
    m_exec = y_m[len(w_alloc): 2*len(w_alloc)]
    temp = y_m[2*len(w_alloc): len(y_m)]

    return m_aux, m_exec, m_busy, temp, res.t, temp_time, res.y


def GLOBAL(m: np.ndarray, a: np.ndarray, b: np.ndarray, bp: np.ndarray, w_alloc: np.ndarray, ma: float):
    res = a.dot(m.reshape((len(m), 1))) + b.dot(w_alloc) + bp * ma
    return res.reshape(len(res))
