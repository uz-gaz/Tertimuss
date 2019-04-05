from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class GlobalSpecification(object):
    """
    Problem global specification
    """

    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                 environment_specification: EnvironmentSpecification,
                 simulation_specification: SimulationSpecification):
        """

        :param tasks_specification: Tasks specification
        :param cpu_specification: Cpu cores and board specification
        :param environment_specification: Environment specification
        :param simulation_specification: Simulation parameters specification
        """
        self.tasks_specification = tasks_specification
        self.cpu_specification = cpu_specification
        self.environment_specification = environment_specification
        self.simulation_specification = simulation_specification
