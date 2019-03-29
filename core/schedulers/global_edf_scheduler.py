from core.kernel_generator.global_model import GlobalModel
from core.kernel_generator.processor_model import ProcessorModel
from core.kernel_generator.tasks_model import TasksModel
from core.kernel_generator.thermal_model import ThermalModel
from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification
from core.schedulers.abstract_scheduler import AbstractScheduler


class GlobalEDFScheduler(AbstractScheduler):

    def __init__(self) -> None:
        super().__init__()

    def simulate(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                 environment_specification: EnvironmentSpecification, simulation_specification: SimulationSpecification,
                 global_model: GlobalModel, processor_model: ProcessorModel, tasks_model: TasksModel,
                 thermal_model: ThermalModel):
        pass