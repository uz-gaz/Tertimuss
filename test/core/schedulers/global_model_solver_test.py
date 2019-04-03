import numpy as np

from core.kernel_generator.global_model import GlobalModel, generate_global_model
from core.kernel_generator.processor_model import generate_processor_model, ProcessorModel
from core.kernel_generator.tasks_model import TasksModel, generate_tasks_model
from core.kernel_generator.thermal_model import ThermalModel, generate_thermal_model
from core.problem_specification_models.CpuSpecification import MaterialCuboid, CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, Task
from core.schedulers.global_model_solver import solve_global_model

mo = [1, 2, 1, 3, 1, 3, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1] + 675 * [45]

mo = np.asarray(mo)

TimeSol: np.ndarray = np.asarray([0, 0.0100000000000000])
TimeSol = TimeSol.reshape((len(TimeSol), 1))

ma: float = 45

w_alloc: np.ndarray = np.asarray(
    [0.250000000000003, 0.187500000000001, 0.125000000000000, 0.250000000000001, 0.187500000000001, 0.125000000000000])

#w_alloc = w_alloc.reshape((len(w_alloc), 1))

tasks_specification: TasksSpecification = TasksSpecification([Task(2, 4, 6.4),
                                                              Task(3, 8, 8),
                                                              Task(3, 12, 9.6)])
cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                       MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                       2, 1)

environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

processor_model: ProcessorModel = generate_processor_model(tasks_specification, cpu_specification)

tasks_model: TasksModel = generate_tasks_model(tasks_specification, cpu_specification)

thermal_model: ThermalModel = generate_thermal_model(tasks_specification, cpu_specification,
                                                     environment_specification,
                                                     simulation_specification)

global_model: GlobalModel = generate_global_model(tasks_model, processor_model, thermal_model,
                                                  environment_specification)

m, m_exec, m_busy, temp, tout, temp_time, m_tcpn = solve_global_model(global_model, mo, w_alloc, ma, TimeSol)

