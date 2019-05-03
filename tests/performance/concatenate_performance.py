import sys
import time
import unittest

import scipy


class PerformanceTests(unittest.TestCase):
    def test_concatenate_performance(self):
        # Concatenate
        where_concatenate = scipy.ndarray((1000, 0))

        iterations = 300

        time1 = time.time()
        for i in range(iterations):
            where_concatenate = scipy.concatenate([where_concatenate, scipy.ones((1000, 1000)) * i], axis=1)

        time2 = time.time()
        size = (sys.getsizeof(where_concatenate)) / 10 ** 6

        print("Concatenate -> time taken:", time2 - time1, "s", ", array size:", size, "MB")

        # Array
        where_concatenate = []

        time.sleep(5)

        time1 = time.time()
        for i in range(iterations):
            where_concatenate.append(scipy.ones((1000, 1000)) * i)

        where_concatenate = scipy.concatenate(where_concatenate, axis=1)
        time2 = time.time()
        size = (sys.getsizeof(where_concatenate)) / 10 ** 6

        print("Array append -> time taken:", time2 - time1, "s", ", array size:", size, "MB")

        """
        Comparison between multiple concatenation of an array of big dimensions and in the other hand add fragments
         to an array and then concatenate it at last time 
        Second must be better, because in the first case, in each addition, the complete array must be moved to a
         continuous space where fit the array size and the new piece.
        In the other hand, in the second case, the array is a linked list, so we don't need to find a continuous space
         where can fit the complete array, we only need to copy the new piece
        
        Results: Laptop Acer aspire 3 a315-51 (CPU Intel Core i3-7020U, RAM 2 * 4 GB 2400 MHz)
        Concatenate -> time taken: 270.4897389411926 s , array size: 2400.000112 MB
        Array append -> time taken: 4.873354434967041 s , array size: 2400.000112 MB
        
        Results: Desktop PC (CPU Intel Pentium E5700 dual core 3.00 GHz, FSB: 800 MHz,
         RAM: 2 * 4 GB 1600 MHz (FSB bottle neck))
         
        Concatenate -> time taken: 392.25426983833313 s , array size: 2400.000112 MB
        Array append -> time taken: 5.727975368499756 s , array size: 2400.000112 MB
        """


if __name__ == '__main__':
    unittest.main()
