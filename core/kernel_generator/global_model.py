import scipy

from core.kernel_generator.processor_model import ProcessorModel
from core.kernel_generator.tasks_model import TasksModel
from core.kernel_generator.thermal_model import ThermalModel
import numpy as np

from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification


class GlobalModel(object):

    def __init__(self, a: np.ndarray, b: np.ndarray, bp: np.ndarray, s: np.ndarray, s_thermal: np.ndarray,
                 mo: np.ndarray):
        self.a = a
        self.b = b
        self.bp = bp
        self.s = s
        self.s_thermal = s_thermal
        self.mo = mo


def generate_global_model(tasks_model: TasksModel, processor_model: ProcessorModel,
                          thermal_model: ThermalModel,
                          environment_specification: EnvironmentSpecification) -> GlobalModel:
    # TODO Improve: Make possible to use without thermal model
    # TODO: Review

    a = scipy.linalg.block_diag(tasks_model.a_tau, processor_model.a_proc, thermal_model.a_t)

    b = np.concatenate((tasks_model.c_tau_alloc, processor_model.c_proc_alloc, thermal_model.ct_exec), axis=1)

    bp = np.concatenate(
        (np.zeros((len(tasks_model.a_tau), 1)), np.zeros((len(processor_model.c_proc_alloc), 1)), thermal_model.b_ta),
        axis=1)

    s = np.concatenate((processor_model.s_busy, processor_model.s_exec), axis=1)
    s = scipy.linalg.block_diag(s, thermal_model.s_t)
    s = np.concatenate((np.zeros((len(s), len(tasks_model.a_tau))), s), axis=1)

    s_thermal = np.zeros((len(thermal_model.a_t), len(tasks_model.a_tau) + len(processor_model.a_proc)))
    s_thermal = np.concatenate((s_thermal, np.identity(len(thermal_model.a_t))), axis=1)

    mo = np.full((len(thermal_model.a_t), 1), environment_specification.t_env)
    mo = np.concatenate((tasks_model.m_tau_o, processor_model.m_proc_o, mo), axis=1)

    return GlobalModel(a, b, bp, s, s_thermal, mo)
