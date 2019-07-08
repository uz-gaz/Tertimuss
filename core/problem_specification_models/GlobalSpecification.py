from typing import Optional

from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TCPNModelSpecification import TCPNModelSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class GlobalSpecification(object):
    """
    Problem global specification
    """

    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                 environment_specification: Optional[EnvironmentSpecification],
                 simulation_specification: SimulationSpecification,
                 tcpn_model_specification: TCPNModelSpecification):
        """

        :param tasks_specification: Tasks specification
        :param cpu_specification: Cpu cores and board specification
        :param environment_specification: Environment specification
        :param simulation_specification: Simulation parameters specification
        :param tcpn_model_specification: Specification of some TCPN optinal parts
        """
        self.tasks_specification: TasksSpecification = tasks_specification
        self.cpu_specification: CpuSpecification = cpu_specification
        self.environment_specification: EnvironmentSpecification = environment_specification
        self.simulation_specification: SimulationSpecification = simulation_specification
        self.tcpn_model_specification: TCPNModelSpecification = tcpn_model_specification
