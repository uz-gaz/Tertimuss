import unittest

from main.core.schedulers.templates.abstract_scheduler.AbstractScheduler import AbstractScheduler

from main.core.schedulers.implementations.G_EDF_A import GlobalEDFAffinityScheduler
from tests.core.schedulers.scheduler_abstract_test import SchedulerAbstractTest


class TestGlobalEdfScheduler(SchedulerAbstractTest):

    @staticmethod
    def get_global_variables() -> [AbstractScheduler, str]:
        # Scheduler
        scheduler = GlobalEDFAffinityScheduler()

        # Result base name
        scheduler_name = "global_edf_a"

        return scheduler, scheduler_name

    def test_with_thermal(self):
        scheduler, scheduler_name = self.get_global_variables()
        # self.run_test_hash_based(scheduler, True, False, "c7fcaeaacde45b20055a789ce174d491")
        self.save_plot_outputs_result(scheduler, True, False, "out/" + scheduler_name + "_thermal")
        # self.save_matlab_result(scheduler, True, False, "out/" + scheduler_name + "_thermal")

    def test_without_thermal(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.run_test_hash_based(scheduler, False, False, "c7fcaeaacde45b20055a789ce174d491")
        # self.save_plot_outputs_result(scheduler, False, False, "out/" + scheduler_name + "_no_thermal")
        # self.save_matlab_result(scheduler, False, False, "out/" + scheduler_name + "_no_thermal")

    def test_with_thermal_and_aperiodics(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.run_test_hash_based(scheduler, True, True, "e81a5f21d4e7ee6bd67e34ec1a57ce77")
        # self.save_plot_outputs_result(scheduler, True, True, "out/" + scheduler_name + "_thermal_and_aperiodics")
        # self.save_matlab_result(scheduler, True, True, "out/" + scheduler_name + "_thermal_and_aperiodics")


if __name__ == '__main__':
    unittest.main()
