from core.kernel_generator.global_model import GlobalModel, generate_global_model
from core.kernel_generator.processor_model import ProcessorModel, generate_processor_model
from core.kernel_generator.tasks_model import generate_tasks_model, TasksModel
from core.kernel_generator.thermal_model import generate_thermal_model, ThermalModel
from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class SimulationKernel(object):
    def __init__(self, tasks_model: TasksModel, processor_model: ProcessorModel, thermal_model: ThermalModel,
                 global_model: GlobalModel):
        self.tasks_model = tasks_model
        self.processor_model = processor_model
        self.thermal_model = thermal_model
        self.global_model = global_model


def generate_kernel(tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                    environment_specification: EnvironmentSpecification,
                    simulation_specification: SimulationSpecification) -> SimulationKernel:
    tasks_model: TasksModel = generate_tasks_model(tasks_specification, cpu_specification)

    processor_model: ProcessorModel = generate_processor_model(tasks_specification, cpu_specification)

    thermal_model: ThermalModel = generate_thermal_model(tasks_specification, cpu_specification,
                                                         environment_specification,
                                                         simulation_specification)

    global_model: GlobalModel = generate_global_model(tasks_model, processor_model, thermal_model,
                                                      environment_specification)

    return SimulationKernel(tasks_model, processor_model, thermal_model, global_model)
