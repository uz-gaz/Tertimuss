from typing import Optional

from scipy import linalg
import scipy

from core.kernel_generator.processor_model import ProcessorModel
from core.kernel_generator.tasks_model import TasksModel
from core.kernel_generator.thermal_model import ThermalModel

from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification


class GlobalModel(object):

    def __init__(self, a: scipy.ndarray, b: scipy.ndarray, bp: scipy.ndarray, s: scipy.ndarray,
                 s_thermal: scipy.ndarray):
        """
        Create a global model
        """
        self.a = a
        self.b = b
        self.bp = bp
        self.s = s
        self.s_thermal = s_thermal


def generate_global_model_with_thermal(tasks_model: TasksModel, processor_model: ProcessorModel,
                                       thermal_model: ThermalModel, environment_specification: EnvironmentSpecification) \
        -> [GlobalModel, scipy.ndarray]:
    a = linalg.block_diag(tasks_model.a_tau, processor_model.a_proc, thermal_model.a_t)

    b = scipy.concatenate((tasks_model.c_tau_alloc, processor_model.c_proc_alloc, thermal_model.ct_exec))

    bp = scipy.concatenate(
        (scipy.zeros((len(tasks_model.a_tau), 1)), scipy.zeros((len(processor_model.c_proc_alloc), 1)),
         thermal_model.b_ta.reshape((len(thermal_model.b_ta), 1))))

    s = scipy.concatenate((processor_model.s_busy, processor_model.s_exec))
    s = linalg.block_diag(s, thermal_model.s_t)
    s = scipy.concatenate((scipy.zeros((len(s), len(tasks_model.a_tau))), s), axis=1)

    s_thermal = scipy.zeros((len(thermal_model.a_t), len(tasks_model.a_tau) + len(processor_model.a_proc)))
    s_thermal = scipy.concatenate((s_thermal, scipy.identity(len(thermal_model.a_t))), axis=1)

    mo = scipy.full((len(thermal_model.a_t), 1), environment_specification.t_env)
    mo = scipy.concatenate((tasks_model.m_tau_o, processor_model.m_proc_o, mo))

    return GlobalModel(a, b, bp, s, s_thermal), mo


def generate_global_model_without_thermal(tasks_model: TasksModel, processor_model: ProcessorModel) -> [GlobalModel,
                                                                                                        scipy.ndarray]:
    a = linalg.block_diag(tasks_model.a_tau, processor_model.a_proc)

    b = scipy.concatenate((tasks_model.c_tau_alloc, processor_model.c_proc_alloc,))

    bp = scipy.concatenate(
        (scipy.zeros((len(tasks_model.a_tau), 1)), scipy.zeros((len(processor_model.c_proc_alloc), 1))))

    s = scipy.concatenate((processor_model.s_busy, processor_model.s_exec))
    s = linalg.block_diag(s)
    s = scipy.concatenate((scipy.zeros((len(s), len(tasks_model.a_tau))), s), axis=1)

    s_thermal = scipy.asarray([])

    mo = scipy.concatenate((tasks_model.m_tau_o, processor_model.m_proc_o))

    return GlobalModel(a, b, bp, s, s_thermal), mo


def generate_global_model(tasks_model: TasksModel, processor_model: ProcessorModel,
                          thermal_model: Optional[ThermalModel], environment_specification: EnvironmentSpecification) \
        -> [GlobalModel, scipy.ndarray]:
    if thermal_model is not None:
        return generate_global_model_with_thermal(tasks_model, processor_model, thermal_model,
                                                  environment_specification)
    else:
        return generate_global_model_without_thermal(tasks_model, processor_model)
