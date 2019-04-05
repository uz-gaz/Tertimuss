from core.kernel_generator.kernel import SimulationKernel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.schedulers.abstract_scheduler import AbstractScheduler


class GlobalEDFScheduler(AbstractScheduler):

    def __init__(self) -> None:
        super().__init__()

    def simulate(self, global_specification: GlobalSpecification, simulation_kernel: SimulationKernel):
        # TODO
        pass
