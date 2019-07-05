import unittest
from core.schedulers.implementations.global_wodes import GlobalWodesScheduler


class GlobalWodes(unittest.TestCase):
    def test_lpp(self):
        ci = [9, 9, 8]
        ti = [10, 10, 40]
        gw = GlobalWodesScheduler()
        s, sd, hyperperiod, isd = gw.ilpp_dp(ci, ti, 3, 2)


if __name__ == '__main__':
    unittest.main()
