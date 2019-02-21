from core.kernel_generator.processor_model import ProcessorModel, generate_processor_model
from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification_models.TasksSpecification import TasksSpecification, Task

tasks_specification: TasksSpecification = TasksSpecification([Task(2, 4, 6.4),
                                                              Task(3, 8, 8),
                                                              Task(3, 12, 9.6)])
cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=2, p=0.2, c_p=1.2, k=0.1),
                                                       MaterialCuboid(x=10, y=10, z=2, p=0.2, c_p=1.2, k=0.1),
                                                       2, 1)

processor_model: ProcessorModel = generate_processor_model(tasks_specification, cpu_specification)
