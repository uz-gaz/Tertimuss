import sys
import time
import unittest

import scipy


class PerformanceTests(unittest.TestCase):
    def test_concatenate_performance(self):
        ## Concatenate
        where_concatenate = scipy.ndarray((1000, 0))

        iterations = 300

        time1 = time.time()
        for i in range(iterations):
            where_concatenate = scipy.concatenate([where_concatenate, scipy.ones((1000, 1000)) * i], axis=1)

        time2 = time.time()
        size = (sys.getsizeof(where_concatenate)) / 10 ** 6

        print("Le ha costado a concatenate:", time2 - time1, "segundos", "y el array pesa", size, "MB")

        ## Array
        where_concatenate = []

        time.sleep(5)

        time1 = time.time()
        for i in range(iterations):
            where_concatenate.append(scipy.ones((1000, 1000)) * i)

        where_concatenate = scipy.concatenate(where_concatenate, axis=1)
        time2 = time.time()
        size = (sys.getsizeof(where_concatenate)) / 10 ** 6

        print("Le ha costado a array:", time2 - time1, "segundos", "y el array pesa", size, "MB")

        """
        Le ha costado a concatenate: 270.4897389411926 segundos y el array pesa 2400.000112 MB
        Le ha costado a array: 4.873354434967041 segundos y el array pesa 2400.000112 MB
        """


if __name__ == '__main__':
    unittest.main()
