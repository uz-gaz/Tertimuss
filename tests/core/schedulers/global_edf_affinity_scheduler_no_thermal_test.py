import unittest

from core.kernel_generator.global_model import generate_global_model_without_thermal
from core.kernel_generator.kernel import SimulationKernel
from core.kernel_generator.processor_model import ProcessorModel, generate_processor_model
from core.kernel_generator.tasks_model import TasksModel, generate_tasks_model
from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, Task
from core.schedulers.global_edf_affinity_scheduler import GlobalEDFAffinityScheduler
from output_generation.output_generator import plot_cpu_utilization, plot_task_execution, \
    plot_accumulated_execution_time


class TestGlobalEdfSchedulerNoThermal(unittest.TestCase):

    def test_global_edf_scheduler_no_thermal(self):
        tasks_specification: TasksSpecification = TasksSpecification([Task(2, 4, None),
                                                                      Task(3, 8, None),
                                                                      Task(3, 12, None)])
        cpu_specification: CpuSpecification = CpuSpecification(None, None, 2, 1)

        simulation_specification: SimulationSpecification = SimulationSpecification(None, 0.01)

        processor_model: ProcessorModel = generate_processor_model(tasks_specification, cpu_specification)

        tasks_model: TasksModel = generate_tasks_model(tasks_specification, cpu_specification)

        global_model, mo = generate_global_model_without_thermal(tasks_model, processor_model)

        simulation_kernel: SimulationKernel = SimulationKernel(tasks_model, processor_model, None, global_model, mo)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        None,
                                                                        simulation_specification)

        scheduler = GlobalEDFAffinityScheduler()

        scheduler_simulation = scheduler.simulate(global_specification, simulation_kernel, None)

        plot_cpu_utilization(global_specification, scheduler_simulation, "affinity_cpu_utilization_no_thermal.png")
        plot_task_execution(global_specification, scheduler_simulation, "affinity_task_execution_no_thermal.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation,
                                        "affinity_accumulated_no_thermal.png")


if __name__ == '__main__':
    unittest.main()
