import functools
import hashlib
import math
import unittest
from typing import List
import numpy

from main.core.schedulers_definition.implementations.AIECS import AIECSScheduler
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler
from tests.core.schedulers.scheduler_abstract_test import SchedulerAbstractTest


class TestJDEDSScheduler(SchedulerAbstractTest):
    @staticmethod
    def list_lcm(values: List[int]) -> int:
        return functools.reduce(lambda a, b: abs(a * b) // math.gcd(a, b), values)

    @staticmethod
    def check_constraints_lpp(cc: List[int], t: List[int], task_execution_by_interval: List[List[int]],
                              intervals_start: List[int]) -> bool:
        hyperperiod = TestJDEDSScheduler.list_lcm(t)

        for task_index, (ci, ti) in enumerate(zip(cc, t)):
            for job_start in range(0, hyperperiod, ti):
                intervals_index = [interval_index for (interval_index, interval_start) in enumerate(intervals_start) if
                                   job_start <= interval_start < job_start + ti]

                if len(intervals_index) > 0:
                    interval_cc = task_execution_by_interval[task_index][intervals_index[0]:intervals_index[-1] + 1]
                    if sum(interval_cc) != ci:
                        return False
                else:
                    return False

        return True

    def test_lpp(self):
        ci = [9, 9, 8]
        ti = [10, 10, 40]
        s, sd = AIECSScheduler.ilpp_dp(ci, ti, 3, 2)

        s_as_integer = [list(map(lambda x: round(x), i)) for i in s.tolist()]
        sd_as_integer = list(map(lambda x: round(x), sd.tolist()))

        assert (self.check_constraints_lpp(ci, ti, s_as_integer, sd_as_integer))

    def test_lpp_2(self):
        ci = [2000, 5000, 6000, 1800]
        ti = [3400, 6800, 10200, 20400]
        s, sd = AIECSScheduler.ilpp_dp(ci, ti, 4, 2)

        s_as_integer = [list(map(lambda x: round(x), i)) for i in s.tolist()]
        sd_as_integer = list(map(lambda x: round(x), sd.tolist()))

        assert (self.check_constraints_lpp(ci, ti, s_as_integer, sd_as_integer))

    def test_lpp_3(self):
        ci = [2, 2, 11, 14]
        ti = [8, 8, 12, 24]

        s, sd = AIECSScheduler.ilpp_dp(ci, ti, 4, 2)

        s_as_integer = [list(map(lambda x: round(x), i)) for i in s.tolist()]
        sd_as_integer = list(map(lambda x: round(x), sd.tolist()))

        assert (self.check_constraints_lpp(ci, ti, s_as_integer, sd_as_integer))

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
