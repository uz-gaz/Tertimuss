import time
import unittest

import scipy


class PerformanceTests(unittest.TestCase):

    def test_performance(self):
        def dot_timed(x: scipy.ndarray, y: scipy.ndarray):
            tim1 = time.time()
            x.dot(y)
            tim2 = time.time()
            print(tim1 - tim2)

        dimension = 1000

        xx = scipy.ones((dimension, dimension), dtype=scipy.float64)
        yy = scipy.ones((dimension, dimension), dtype=scipy.float64)

        dot_timed(xx, yy)


if __name__ == '__main__':
    unittest.main()
