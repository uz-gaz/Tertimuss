import unittest

from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.schedulers_definition.implementations.RUNA import RUNAScheduler
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler

from tests.old.core.schedulers.scheduler_abstract_test import SchedulerAbstractTest


class TestGEDFScheduler(SchedulerAbstractTest):

    @staticmethod
    def get_global_variables() -> [AbstractScheduler, str]:
        # Scheduler
        scheduler = RUNAScheduler(PeriodicTask(1000000, 12, 12, 9.6))

        # Result base name
        scheduler_name = "runa"

        return scheduler, scheduler_name

    def test_without_thermal(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.save_plot_outputs_result(scheduler, False, False, "out/" + scheduler_name + "_no_thermal")
        # self.save_matlab_result(scheduler, False, False, "out/" + scheduler_name + "_no_thermal")

    def test_with_aperiodic(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.save_plot_outputs_result(scheduler, False, True, "out/" + scheduler_name + "_aperiodic")
        # self.save_matlab_result(scheduler, True, True, "out/" + scheduler_name + "_thermal_and_aperiodic")


if __name__ == '__main__':
    unittest.main()
