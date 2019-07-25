from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.environment_specification.EnvironmentSpecification import EnvironmentSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.simulation_specification.TCPNModelSpecification import TCPNModelSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification


class GlobalSpecification(object):

    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                 environment_specification: EnvironmentSpecification,
                 simulation_specification: SimulationSpecification,
                 tcpn_model_specification: TCPNModelSpecification):
        """
        Problem global specification

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
