import unittest

from tertimuss.tasks_generator.deadline_generator import UniformIntegerDeadlineGenerator
from tertimuss.tasks_generator.periodic_tasks.implicit_deadlines import UUniFast


class UUnifastTest(unittest.TestCase):
    def test_uunifast(self):
        cpu_frequency = 100
        tasks_deadlines = UniformIntegerDeadlineGenerator.generate(number_of_tasks=10, min_deadline=2, max_deadline=12,
                                                                   major_cycle=24)
        x = UUniFast.generate(utilization=1, tasks_deadlines=tasks_deadlines, processor_frequency=cpu_frequency)

        assert (0.98 <= sum([i.worst_case_execution_time / (i.deadline * cpu_frequency) for i in x]) <= 1)
        assert (all(i.worst_case_execution_time <= i.deadline * cpu_frequency for i in x))
        assert (all(i.worst_case_execution_time >= 0 for i in x))
