import unittest

from core.schedulers.global_wodes_scheduler import GlobalWodesScheduler


class MyTestCase(unittest.TestCase):
    def test_something(self):
        ci = [2000, 5000, 6000, 1800]
        ti = [3400, 6800, 10200, 20400]
        gw = GlobalWodesScheduler()
        gw.ilpp_dp(ci, ti, 4, 2)


if __name__ == '__main__':
    unittest.main()
