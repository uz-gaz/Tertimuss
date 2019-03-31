import numpy as np
import scipy.integrate

from core.kernel_generator.global_model import GlobalModel


def solve_global_model(global_model: GlobalModel, mo: np.ndarray, w_alloc: np.ndarray, ma: float,
                       time_sol: np.ndarray) -> [np.ndarray, np.ndarray, np.ndarray,
                                                 np.ndarray, np.ndarray,
                                                 np.ndarray, np.ndarray]:
    res = scipy.integrate.solve_ivp(
        lambda t, m: GLOBAL(m, global_model.a, global_model.b, global_model.bp, w_alloc, ma), time_sol, mo
    ) # Review final dimensions

    # TODO: Continue
    pass


def GLOBAL(m: np.ndarray, a: np.ndarray, b: np.ndarray, bp: np.ndarray, w_alloc: np.ndarray, ma: float):
    res = a.dot(m.reshape((len(m), 1))) + b.dot(w_alloc) + bp * ma
    return res.reshape(len(res))
