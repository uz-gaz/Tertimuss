import numpy as np
import scipy.integrate

from core.kernel_generator.global_model import GlobalModel


def solve_global_model(global_model: GlobalModel, mo: np.ndarray, walloc: np.ndarray, ma: float,
                       TimeSol: np.ndarray) -> [np.ndarray, np.ndarray, np.ndarray,
                                                np.ndarray, np.ndarray,
                                                np.ndarray, np.ndarray]:
    scipy.integrate.ode(lambda t, m: GLOBAL(m, global_model.a, global_model.b, global_model.bp, walloc,
                                            ma))  # TODO: Analyze and use mo and TimeSol

    # TODO: Continue
    pass


def GLOBAL(m, a: np.ndarray, b: np.ndarray, bp: np.ndarray, walloc: np.ndarray, ma: np.ndarray):
    return a.dot(m) + b.dot(walloc) + bp.dot(ma)
