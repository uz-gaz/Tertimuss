from ._cpu_specification import CpuSpecification
from ._environment_specification import EnvironmentSpecification
from ._simulation_specification import SimulationSpecification
from ._tasks_specification import TasksSpecification


class SystemConfigurationSpecification(object):

    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                 environment_specification: EnvironmentSpecification,
                 simulation_specification: SimulationSpecification):
        """
        Problem specification

        :param tasks_specification: Tasks specification
        :param cpu_specification: Cpu cores and board specification
        :param environment_specification: Environment specification
        :param simulation_specification: Simulation parameters specification
        """
        self.tasks_specification: TasksSpecification = tasks_specification
        self.cpu_specification: CpuSpecification = cpu_specification
        self.environment_specification: EnvironmentSpecification = environment_specification
        self.simulation_specification: SimulationSpecification = simulation_specification
