import unittest

from core.schedulers.implementations.global_jdeds import GlobalJDEDSScheduler
from core.schedulers.templates.abstract_scheduler import AbstractScheduler
from tests.core.schedulers.scheduler_abstract_test import SchedulerAbstractTest


class GlobalWodes(SchedulerAbstractTest):
    def test_lpp(self):
        ci = [9, 9, 8]
        ti = [10, 10, 40]
        s, sd, hyperperiod, isd = GlobalJDEDSScheduler.ilpp_dp(ci, ti, 3, 2)

    def test_lpp_2(self):
        ci = [2000, 5000, 6000, 1800]
        ti = [3400, 6800, 10200, 20400]
        s, sd, hyperperiod, isd = GlobalJDEDSScheduler.ilpp_dp(ci, ti, 4, 2)

    @staticmethod
    def get_global_variables() -> [AbstractScheduler, str]:
        # Scheduler
        scheduler = GlobalJDEDSScheduler()

        # Result base name
        scheduler_name = "global_jdeds"

        return scheduler, scheduler_name

    def test_with_thermal(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.run_test_hash_based(scheduler, True, False, "c7fcaeaacde45b20055a789ce174d491")
        # self.save_plot_outputs_result(scheduler, True, False, "out/" + scheduler_name + "_thermal")
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
