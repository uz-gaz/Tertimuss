import unittest

from tertimuss_plot_generator import generate_task_assignation_plot, generate_job_assignation_plot
from ._generate_simulation_result import get_simulation_result


class AssignationPlotTest(unittest.TestCase):
    def test_tasks_assignation_plot(self):
        tasks, _, simulation_result = get_simulation_result()

        fig = generate_task_assignation_plot(task_set=tasks, schedule_result=simulation_result,
                                             title="Task assignation")
        fig.show()

    def test_job_assignation_plot(self):
        tasks, jobs_list, simulation_result = get_simulation_result()

        fig = generate_job_assignation_plot(task_set=tasks, schedule_result=simulation_result, jobs=jobs_list,
                                            title="Job assignation")
        fig.show()
