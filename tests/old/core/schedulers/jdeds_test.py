import functools
import math
import time
import unittest
from typing import List

from main.core.schedulers_definition.implementations.AIECS import AIECSScheduler
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler
from tests.old.core.schedulers.scheduler_abstract_test import SchedulerAbstractTest


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

    def test_lpp_scipy(self):
        ci = [9, 9, 8]
        ti = [10, 10, 40]
        s, sd = AIECSScheduler.aiecs_periods_lpp_scipy(ci, ti, len(ti), 2)
        assert (self.check_constraints_lpp(ci, ti, sd, s))

    def test_lpp_glop(self):
        ci = [9, 9, 8]
        ti = [10, 10, 40]
        s, sd = AIECSScheduler.aiecs_periods_lpp(ci, ti, 2)
        assert (self.check_constraints_lpp(ci, ti, sd, s))

    def test_lpp_scipy_performance_4_24(self):
        start_time = time.perf_counter()
        ci = [570, 1880, 166, 1416, 2160, 36, 112, 780, 1430, 1044, 720, 436, 1940, 239, 1388, 2480, 1705, 4480, 820,
              5820, 956, 220, 600, 254]
        ti = [10000, 40000, 2000, 8000, 40000, 2000, 1000, 4000, 5000, 4000, 8000, 4000, 20000, 1000, 2000, 10000, 5000,
              40000, 10000, 20000, 4000, 20000, 20000, 2000]
        s, sd = AIECSScheduler.aiecs_periods_lpp_scipy(ci, ti, len(ti), 4)
        end_time = time.perf_counter()
        assert (self.check_constraints_lpp(ci, ti, sd, s))
        print("Elapsed time:", end_time - start_time)
        # Elapsed time: 67.22464067200008

    def test_lpp_glop_performance_4_24(self):
        start_time = time.perf_counter()
        ci = [570, 1880, 166, 1416, 2160, 36, 112, 780, 1430, 1044, 720, 436, 1940, 239, 1388, 2480, 1705, 4480, 820,
              5820, 956, 220, 600, 254]
        ti = [10000, 40000, 2000, 8000, 40000, 2000, 1000, 4000, 5000, 4000, 8000, 4000, 20000, 1000, 2000, 10000,
              5000,
              40000, 10000, 20000, 4000, 20000, 20000, 2000]
        s, sd = AIECSScheduler.aiecs_periods_lpp_glop(ci, ti, 4)
        end_time = time.perf_counter()
        assert (self.check_constraints_lpp(ci, ti, sd, s))
        print("Elapsed time:", end_time - start_time)
        # Elapsed time: 0.04560911099997611 s

    def test_lpp_scipy_performance_4_32(self):
        start_time = time.perf_counter()
        ci = [1380, 2320, 888, 139, 768, 1050, 740, 920, 1600, 152, 760, 5820, 1016, 91, 2880, 1820, 53, 2990, 77, 3520,
              596, 84, 3260, 2340, 652, 24, 486, 464, 730, 460, 67, 136]
        ti = [20000, 40000, 4000, 1000, 8000, 10000, 10000, 10000, 20000, 1000, 40000, 20000, 8000, 1000, 40000, 20000,
              1000, 10000, 1000, 40000, 4000, 1000, 20000, 10000, 4000, 4000, 1000, 8000, 5000, 4000, 1000, 4000]

        s, sd = AIECSScheduler.aiecs_periods_lpp_scipy(ci, ti, len(ti), 4)
        end_time = time.perf_counter()
        assert (self.check_constraints_lpp(ci, ti, sd, s))
        print("Elapsed time:", end_time - start_time)
        # Elapsed time: 157.7277492809999 s

    def test_lpp_glop_performance_4_32(self):
        start_time = time.perf_counter()
        ci = [1380, 2320, 888, 139, 768, 1050, 740, 920, 1600, 152, 760, 5820, 1016, 91, 2880, 1820, 53, 2990, 77, 3520,
              596, 84, 3260, 2340, 652, 24, 486, 464, 730, 460, 67, 136]
        ti = [20000, 40000, 4000, 1000, 8000, 10000, 10000, 10000, 20000, 1000, 40000, 20000, 8000, 1000, 40000, 20000,
              1000, 10000, 1000, 40000, 4000, 1000, 20000, 10000, 4000, 4000, 1000, 8000, 5000, 4000, 1000, 4000]

        s, sd = AIECSScheduler.aiecs_periods_lpp_glop(ci, ti, 4)
        end_time = time.perf_counter()
        assert (self.check_constraints_lpp(ci, ti, sd, s))
        print("Elapsed time:", end_time - start_time)
        # Elapsed time: 0.06159063300037815 s

    def test_lpp_scipy_performance_4_40(self):
        start_time = time.perf_counter()
        ci = [24, 480, 210, 156, 440, 3640, 72, 7280, 365, 1064, 264, 1180, 775, 1380, 6120, 7060, 84, 568, 7440, 66,
              400, 335, 172, 135, 45, 305, 2010, 4420, 152, 344, 1480, 348, 60, 698, 104, 1420, 460, 6880, 1260, 98]
        ti = [2000, 8000, 10000, 2000, 20000, 20000, 8000, 40000, 5000, 8000, 4000, 20000, 5000, 20000, 40000, 20000,
              1000, 8000, 40000, 1000, 40000, 5000, 4000, 5000, 5000, 5000, 10000, 20000, 2000, 8000, 40000, 1000, 1000,
              2000, 8000, 20000, 10000, 40000, 20000, 2000]
        s, sd = AIECSScheduler.aiecs_periods_lpp_scipy(ci, ti, len(ti), 4)
        end_time = time.perf_counter()
        assert (self.check_constraints_lpp(ci, ti, sd, s))
        print("Elapsed time:", end_time - start_time)
        # Elapsed time: 345.6934918320003 s

    def test_lpp_glop_performance_4_40(self):
        start_time = time.perf_counter()
        ci = [24, 480, 210, 156, 440, 3640, 72, 7280, 365, 1064, 264, 1180, 775, 1380, 6120, 7060, 84, 568, 7440, 66,
              400, 335, 172, 135, 45, 305, 2010, 4420, 152, 344, 1480, 348, 60, 698, 104, 1420, 460, 6880, 1260, 98]
        ti = [2000, 8000, 10000, 2000, 20000, 20000, 8000, 40000, 5000, 8000, 4000, 20000, 5000, 20000, 40000, 20000,
              1000, 8000, 40000, 1000, 40000, 5000, 4000, 5000, 5000, 5000, 10000, 20000, 2000, 8000, 40000, 1000, 1000,
              2000, 8000, 20000, 10000, 40000, 20000, 2000]
        s, sd = AIECSScheduler.aiecs_periods_lpp_glop(ci, ti, 4)
        end_time = time.perf_counter()
        assert (self.check_constraints_lpp(ci, ti, sd, s))
        print("Elapsed time:", end_time - start_time)
        # Elapsed time: 0.07723052999972424 s

    def test_lpp_scipy_performance_8_48(self):
        start_time = time.perf_counter()
        ci = [287, 950, 430, 245, 930, 4840, 3920, 419, 486, 250, 260, 4488, 3380, 345, 4820, 605, 422, 1780, 368, 44,
              1110, 16880, 395, 416, 780, 134, 45, 6040, 11760, 1420, 425, 330, 672, 2700, 250, 840, 40, 960, 415, 716,
              3232, 3400, 255, 4680, 350, 404, 38, 70]
        ti = [1000, 10000, 5000, 1000, 10000, 40000, 20000, 1000, 2000, 10000, 20000, 8000, 20000, 5000, 20000, 5000,
              2000, 20000, 8000, 1000, 5000, 40000, 5000, 8000, 5000, 2000, 5000, 40000, 20000, 10000, 5000, 5000, 4000,
              20000, 2000, 10000, 2000, 20000, 1000, 4000, 8000, 10000, 5000, 20000, 2000, 4000, 1000, 1000]

        s, sd = AIECSScheduler.aiecs_periods_lpp_scipy(ci, ti, len(ti), 8)
        end_time = time.perf_counter()
        assert (self.check_constraints_lpp(ci, ti, sd, s))
        print("Elapsed time:", end_time - start_time)
        # Elapsed time: 638.5175364530005 s

    def test_lpp_glop_performance_8_48(self):
        start_time = time.perf_counter()
        ci = [287, 950, 430, 245, 930, 4840, 3920, 419, 486, 250, 260, 4488, 3380, 345, 4820, 605, 422, 1780, 368, 44,
              1110, 16880, 395, 416, 780, 134, 45, 6040, 11760, 1420, 425, 330, 672, 2700, 250, 840, 40, 960, 415, 716,
              3232, 3400, 255, 4680, 350, 404, 38, 70]
        ti = [1000, 10000, 5000, 1000, 10000, 40000, 20000, 1000, 2000, 10000, 20000, 8000, 20000, 5000, 20000, 5000,
              2000, 20000, 8000, 1000, 5000, 40000, 5000, 8000, 5000, 2000, 5000, 40000, 20000, 10000, 5000, 5000, 4000,
              20000, 2000, 10000, 2000, 20000, 1000, 4000, 8000, 10000, 5000, 20000, 2000, 4000, 1000, 1000]

        s, sd = AIECSScheduler.aiecs_periods_lpp_glop(ci, ti, 8)
        end_time = time.perf_counter()
        assert (self.check_constraints_lpp(ci, ti, sd, s))
        print("Elapsed time:", end_time - start_time)
        # Elapsed time: 0.09485625300021638 s

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
