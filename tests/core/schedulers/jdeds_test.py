import hashlib
import unittest

from main.core.schedulers_definition.implementations.AIECS import AIECSScheduler
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler
from tests.core.schedulers.scheduler_abstract_test import SchedulerAbstractTest


class TestJDEDSScheduler(SchedulerAbstractTest):
    def test_lpp(self):
        ci = [9, 9, 8]
        ti = [10, 10, 40]
        s, sd = AIECSScheduler.ilpp_dp(ci, ti, 3, 2)
        self.assertEqual(hashlib.md5(s).hexdigest(), "f47db2f641bd29f0bf3498d66e3c3790")
        self.assertEqual(hashlib.md5(sd).hexdigest(), "4328c1ee6f725e907c587b83207c58a7")

    def test_lpp_2(self):
        ci = [2000, 5000, 6000, 1800]
        ti = [3400, 6800, 10200, 20400]
        s, sd = AIECSScheduler.ilpp_dp(ci, ti, 4, 2)
        self.assertEqual(hashlib.md5(s).hexdigest(), "b00512bd9e6bd7d8a556a764680f896f")
        self.assertEqual(hashlib.md5(sd).hexdigest(), "c2063acec2becad2e60db08968f16fad")

    def test_lpp_3(self):
        ci = [2, 2, 11, 14]
        ti = [8, 8, 12, 24]
        s, sd = AIECSScheduler.ilpp_dp(ci, ti, 4, 2)

    @staticmethod
    def get_global_variables() -> [AbstractScheduler, str]:
        # Scheduler
        scheduler = AIECSScheduler()

        # Result base name
        scheduler_name = "jdeds"

        return scheduler, scheduler_name

    def test_with_thermal(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.save_plot_outputs_result(scheduler, True, False, "out/" + scheduler_name + "_thermal")
        # self.save_matlab_result(scheduler, True, False, "out/" + scheduler_name + "_thermal")

    def test_without_thermal(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.save_plot_outputs_result(scheduler, False, False, "out/" + scheduler_name + "_no_thermal")
        # self.save_matlab_result(scheduler, False, False, "out/" + scheduler_name + "_no_thermal")

    def test_with_thermal_and_aperiodic(self):
        scheduler, scheduler_name = self.get_global_variables()
        self.save_plot_outputs_result(scheduler, True, True, "out/" + scheduler_name + "_thermal_and_aperiodic")
        # self.save_matlab_result(scheduler, True, True, "out/" + scheduler_name + "_thermal_and_aperiodic")


if __name__ == '__main__':
    unittest.main()
