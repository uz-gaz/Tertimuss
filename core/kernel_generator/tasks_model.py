from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class TasksModel(object):
    def __init__(self, c_tau, lambda_tau, pi_tau, c_tau_alloc, m_tau_o):
        self.c_tau = c_tau
        self.lambda_tau = lambda_tau
        self.pi_tau = pi_tau
        self.c_tau_alloc = c_tau_alloc
        self.m_tau_o = m_tau_o


def generate_tasks_model(tasks_specification: TasksSpecification, cpu_specification: CpuSpecification) -> TasksModel:
    pass
