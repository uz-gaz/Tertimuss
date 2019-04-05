from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class GlobalSpecification(object):

    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                 environment_specification: EnvironmentSpecification,
                 simulation_specification: SimulationSpecification):
        self.tasks_specification = tasks_specification
        self.cpu_specification = cpu_specification
        self.environment_specification = environment_specification
        self.simulation_specification = simulation_specification
