import unittest

from ._generate_simulation_result import get_simulation_result

from tertimuss.visualization_generator import generate_accumulate_execution_plot, \
    generate_job_accumulate_execution_plot


class AccumulateExecutionPlotTest(unittest.TestCase):
    # @unittest.skip("Manual visualization test")
    def test_tasks_accumulate_execution_plot(self):
        tasks, _, simulation_result = get_simulation_result()

        fig = generate_accumulate_execution_plot(task_set=tasks, schedule_result=simulation_result,
                                                 title="Task accumulate execution")
        # fig.show()

    # @unittest.skip("Manual visualization test")
    def test_job_accumulate_execution_plot(self):
        tasks, jobs_list, simulation_result = get_simulation_result()

        fig = generate_job_accumulate_execution_plot(task_set=tasks, schedule_result=simulation_result, jobs=jobs_list,
                                                     title="Job accumulate execution")
        # fig.show()
