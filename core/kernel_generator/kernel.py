import scipy

from core.kernel_generator.global_model import GlobalModel, generate_global_model
from core.kernel_generator.processor_model import ProcessorModel, generate_processor_model
from core.kernel_generator.tasks_model import generate_tasks_model, TasksModel
from core.kernel_generator.thermal_model import generate_thermal_model, ThermalModel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification


class SimulationKernel(object):
    """
    Encapsulate all TCPN which represent the kernel
    """
    def __init__(self, tasks_model: TasksModel, processor_model: ProcessorModel, thermal_model: ThermalModel,
                 global_model: GlobalModel, mo: scipy.ndarray):
        self.tasks_model = tasks_model
        self.processor_model = processor_model
        self.thermal_model = thermal_model
        self.global_model = global_model
        self.mo = mo


def generate_kernel(global_specification: GlobalSpecification) -> SimulationKernel:
    tasks_model: TasksModel = generate_tasks_model(global_specification.tasks_specification,
                                                   global_specification.cpu_specification)

    processor_model: ProcessorModel = generate_processor_model(global_specification.tasks_specification,
                                                               global_specification.cpu_specification)

    thermal_model: ThermalModel = generate_thermal_model(global_specification.tasks_specification,
                                                         global_specification.cpu_specification,
                                                         global_specification.environment_specification,
                                                         global_specification.simulation_specification)

    global_model, mo = generate_global_model(tasks_model, processor_model, thermal_model,
                                             global_specification.environment_specification)

    return SimulationKernel(tasks_model, processor_model, thermal_model, global_model, mo)
