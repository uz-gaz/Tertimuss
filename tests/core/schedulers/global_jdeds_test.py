import hashlib
import unittest

from main.core.schedulers.implementations.JDEDS import GlobalJDEDSScheduler
from main.core.schedulers.templates.abstract_scheduler.AbstractScheduler import AbstractScheduler
from tests.core.schedulers.scheduler_abstract_test import SchedulerAbstractTest


class GlobalWodes(SchedulerAbstractTest):
    def test_lpp(self):
        ci = [9, 9, 8]
        ti = [10, 10, 40]
        s, sd, _, _ = GlobalJDEDSScheduler.ilpp_dp(ci, ti, 3, 2)
        self.assertEqual(hashlib.md5(s).hexdigest(), "f47db2f641bd29f0bf3498d66e3c3790")
        self.assertEqual(hashlib.md5(sd).hexdigest(), "4328c1ee6f725e907c587b83207c58a7")

    def test_lpp_2(self):
        ci = [2000, 5000, 6000, 1800]
        ti = [3400, 6800, 10200, 20400]
        s, sd, _, _ = GlobalJDEDSScheduler.ilpp_dp(ci, ti, 4, 2)
        self.assertEqual(hashlib.md5(s).hexdigest(), "b00512bd9e6bd7d8a556a764680f896f")
        self.assertEqual(hashlib.md5(sd).hexdigest(), "c2063acec2becad2e60db08968f16fad")

    @staticmethod
    def get_global_variables() -> [AbstractScheduler, str]:
        # Scheduler
        scheduler = GlobalJDEDSScheduler()

        # Result base name
        scheduler_name = "global_jdeds"

        return scheduler, scheduler_name

    def test_with_thermal(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.run_test_hash_based(scheduler, True, False, "4d75f3bd66de2ee05531c062f4c73e74")
        # self.save_plot_outputs_result(scheduler, True, False, "out/" + scheduler_name + "_thermal")
        # self.save_matlab_result(scheduler, True, False, "out/" + scheduler_name + "_thermal")

    def test_without_thermal(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.run_test_hash_based(scheduler, False, False, "4d75f3bd66de2ee05531c062f4c73e74")
        # self.save_plot_outputs_result(scheduler, False, False, "out/" + scheduler_name + "_no_thermal")
        # self.save_matlab_result(scheduler, False, False, "out/" + scheduler_name + "_no_thermal")

    def test_with_thermal_and_aperiodic(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.run_test_hash_based(scheduler, True, True, "41c38748ec4f1f09f679c6d9c010d6d0")
        # self.save_plot_outputs_result(scheduler, True, True, "out/" + scheduler_name + "_thermal_and_aperiodic")
        # self.save_matlab_result(scheduler, True, True, "out/" + scheduler_name + "_thermal_and_aperiodic")


if __name__ == '__main__':
    unittest.main()
