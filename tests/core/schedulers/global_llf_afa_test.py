import unittest

from main.core.schedulers.implementations.G_LLF_AFA import GlobalLeastLaxityFirstAFAScheduler
from main.core.schedulers.templates.abstract_scheduler.AbstractScheduler import AbstractScheduler
from tests.core.schedulers.scheduler_abstract_test import SchedulerAbstractTest


class TestGlobalLlfAfaScheduler(SchedulerAbstractTest):

    @staticmethod
    def get_global_variables() -> [AbstractScheduler, str]:
        # Scheduler
        scheduler = GlobalLeastLaxityFirstAFAScheduler()

        # Result base name
        scheduler_name = "global_llf_afa"

        return scheduler, scheduler_name

    def test_with_thermal(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.run_test_hash_based(scheduler, True, False, "fda1970bc4a05c97e042718b4d16da87")
        # self.save_plot_outputs_result(scheduler, True, False, "out/" + scheduler_name + "_thermal")
        # self.save_matlab_result(scheduler, True, False, "out/" + scheduler_name + "_thermal")

    def test_without_thermal(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.run_test_hash_based(scheduler, False, False, "fda1970bc4a05c97e042718b4d16da87")
        # self.save_plot_outputs_result(scheduler, False, False, "out/" + scheduler_name + "_no_thermal")
        # self.save_matlab_result(scheduler, False, False, "out/" + scheduler_name + "_no_thermal")

    def test_with_thermal_and_aperiodic(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.run_test_hash_based(scheduler, True, True, "33203916781c207062d8d3d8e9e68d7c")
        # self.save_plot_outputs_result(scheduler, True, True, "out/" + scheduler_name + "_thermal_and_aperiodic")
        # self.save_matlab_result(scheduler, True, True, "out/" + scheduler_name + "_thermal_and_aperiodic")


if __name__ == '__main__':
    unittest.main()
