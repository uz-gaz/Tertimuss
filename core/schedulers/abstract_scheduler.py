import abc

from core.kernel_generator.kernel import SimulationKernel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification


class AbstractScheduler(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def simulate(self, global_specification: GlobalSpecification, simulation_kernel: SimulationKernel):
        pass
