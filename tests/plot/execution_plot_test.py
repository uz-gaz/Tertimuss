import unittest

from tertimuss.plot_generator import generate_task_execution_plot, generate_job_execution_plot
from ._generate_simulation_result import get_simulation_result


class ExecutionPlotTest(unittest.TestCase):
    def test_tasks_execution_plot(self):
        tasks, _, simulation_result = get_simulation_result()

        fig = generate_task_execution_plot(task_set=tasks, schedule_result=simulation_result,
                                           title="Task execution")
        fig.show()

    def test_job_assignation_plot(self):
        tasks, jobs_list, simulation_result = get_simulation_result()

        fig = generate_job_execution_plot(task_set=tasks, schedule_result=simulation_result, jobs=jobs_list,
                                          title="Job execution")
        fig.show()
