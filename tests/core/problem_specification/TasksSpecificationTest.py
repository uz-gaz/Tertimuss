import unittest

from core.problem_specification_models.TasksSpecification import TasksSpecification, PeriodicTask, AperiodicTask


class TaskSpecificationTests(unittest.TestCase):

    def test_task_specification(self):
        te: TasksSpecification = TasksSpecification(
            [PeriodicTask(1, 5, 1, 1), PeriodicTask(1, 10, 1, 1), PeriodicTask(1, 20, 1, 1), AperiodicTask(1, 2, 3, 4)])

        pass


if __name__ == '__main__':
    unittest.main()
