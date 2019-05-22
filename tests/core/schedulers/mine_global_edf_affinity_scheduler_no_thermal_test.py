import unittest

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, Task
from core.schedulers.mine_abstract_global_scheduler import AbstractGlobalScheduler
from output_generation.output_generator import plot_cpu_utilization, plot_task_execution, \
    plot_accumulated_execution_time


class TestGlobalEdfSchedulerNoThermal(unittest.TestCase):

    def test_global_edf_scheduler_no_thermal(self):
        tasks_specification: TasksSpecification = TasksSpecification([Task(2, 4, None),
                                                                      Task(3, 8, None),
                                                                      Task(3, 12, None)])
        cpu_specification: CpuSpecification = CpuSpecification(None, None, 2, 1)

        simulation_specification: SimulationSpecification = SimulationSpecification(None, 0.01)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        None,
                                                                        simulation_specification)

        global_model = GlobalModel(global_specification)

        scheduler = AbstractGlobalScheduler()

        scheduler_simulation = scheduler.simulate(global_specification, global_model, None)

        plot_cpu_utilization(global_specification, scheduler_simulation, "affinity_cpu_utilization_no_thermal.png")
        plot_task_execution(global_specification, scheduler_simulation, "affinity_task_execution_no_thermal.png")
        plot_accumulated_execution_time(global_specification, scheduler_simulation,
                                        "affinity_accumulated_no_thermal.png")


if __name__ == '__main__':
    unittest.main()
