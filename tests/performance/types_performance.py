import sys
import time
import unittest

import scipy


class PerformanceTests(unittest.TestCase):

    def dot_profile_memory_and_time(self, iterations: int, dimension: int, dtype_1, dtype_2) -> [float, float]:
        def dot_timed(x: scipy.ndarray, y: scipy.ndarray):
            tim1 = time.time()
            scipy.dot(x, y)
            tim2 = time.time()
            return tim2 - tim1

        xx = scipy.ones((dimension, dimension), dtype=dtype_1)
        yy = scipy.ones((dimension, dimension), dtype=dtype_2)

        # Size in MB
        size = (sys.getsizeof(xx) + sys.getsizeof(yy)) / 10 ** 6

        # Time in seconds
        time_accumulated = sum(map(lambda _: dot_timed(xx, yy), range(iterations))) / iterations

        return size, time_accumulated

    def test_performance(self):
        types_to_test = [
            #    [scipy.float64, scipy.float64],
            #    [scipy.float32, scipy.float32],
            #    [scipy.bool8, scipy.float64],
            #    [scipy.bool8, scipy.float32],
            [scipy.int8, scipy.float32]
        ]
        iterations = 5
        dimension = 5000
        sleep_between_iterations = 0

        for i in types_to_test:
            time.sleep(sleep_between_iterations)
            size, time_accumulated = self.dot_profile_memory_and_time(iterations, dimension, i[0], i[1])
            print("Profiled", i[0], i[1], "->", "time:", time_accumulated, ", size:", size)

        """
        Results: Desktop PC (CPU Intel Pentium E5700 dual core 3.00 GHz, FSB: 800 MHz,
         RAM: 2 * 4 GB 1600 Mhz (FSB bottle neck))
        
        types_to_test = [
            [scipy.float64, scipy.float64],
            [scipy.float32, scipy.float32],
            [scipy.float16, scipy.float16],
            [scipy.float128, scipy.float128],
            [scipy.bool8, scipy.float64],
            [scipy.int64, scipy.float64],
            [scipy.int64, scipy.int64],
            [scipy.int16, scipy.int16]
        ]
        iterations = 10
        dimension = 4000
        sleep_between_iterations = 10
        
        Profiled <class 'numpy.float64'> <class 'numpy.float64'> -> time: 14.44426417350769 , size: 256.000224
        Profiled <class 'numpy.float32'> <class 'numpy.float32'> -> time: 7.4127590417861935 , size: 128.000224
        
        Don't wait for the rest
        
        
        
        types_to_test = [
            [scipy.float64, scipy.float64],
            [scipy.float32, scipy.float32],
            [scipy.float16, scipy.float16],
            [scipy.float128, scipy.float128],
            [scipy.bool8, scipy.float64],
            [scipy.int64, scipy.float64],
            [scipy.int64, scipy.int64],
            [scipy.int16, scipy.int16]
        ]
        iterations = 1
        dimension = 100
        sleep_between_iterations = 5
        Profiled <class 'numpy.float64'> <class 'numpy.float64'> -> time: 0.23923468589782715 , size: 16.000224
        Profiled <class 'numpy.float32'> <class 'numpy.float32'> -> time: 0.06416511535644531 , size: 8.000224
        Profiled <class 'numpy.float16'> <class 'numpy.float16'> -> time: 11.834898471832275 , size: 4.000224
        Profiled <class 'numpy.float128'> <class 'numpy.float128'> -> time: 9.416418075561523 , size: 32.000224
        Profiled <class 'numpy.bool_'> <class 'numpy.float64'> -> time: 0.24097752571105957 , size: 9.000224
        Profiled <class 'numpy.int64'> <class 'numpy.float64'> -> time: 0.2407517433166504 , size: 16.000224
        Profiled <class 'numpy.int64'> <class 'numpy.int64'> -> time: 5.974678039550781 , size: 16.000224
        Profiled <class 'numpy.int16'> <class 'numpy.int16'> -> time: 2.972834587097168 , size: 4.000224
        
        
        types_to_test = [
            [scipy.float64, scipy.float64],
            [scipy.float32, scipy.float32],
            [scipy.bool8, scipy.float64],
            [scipy.int64, scipy.float64],
            [scipy.int64, scipy.int64],
            [scipy.int32, scipy.int32]
        ]
        iterations = 1
        dimension = 4000
        sleep_between_iterations = 7
        Profiled <class 'numpy.float64'> <class 'numpy.float64'> -> time: 13.99812650680542 , size: 256.000224
        Profiled <class 'numpy.float32'> <class 'numpy.float32'> -> time: 6.890538215637207 , size: 128.000224
        Profiled <class 'numpy.bool_'> <class 'numpy.float64'> -> time: 14.378939151763916 , size: 144.000224
        Profiled <class 'numpy.int64'> <class 'numpy.float64'> -> time: 14.077426433563232 , size: 256.000224
        
        
        https://stackoverflow.com/questions/11856293/numpy-dot-product-very-slow-using-ints
        https://software.intel.com/en-us/mkl-developer-reference-c-naming-conventions-for-blas-routines
        https://software.intel.com/en-us/mkl-developer-reference-c-blas-level-3-routines
        
         Siguiendo ese hilo, me di cuenta de que solamente están optimizados mediante mkl los tipos 
         float32, float64, complex64, y complex128
         
         types_to_test = [
            [scipy.float64, scipy.float64],
            [scipy.float32, scipy.float32],
            [scipy.bool8, scipy.float64],
            [scipy.bool8, scipy.float32],
            [scipy.int8, scipy.float32]
        ]
        iterations = 1
        dimension = 5000
        sleep_between_iterations = 7
        Profiled <class 'numpy.float64'> <class 'numpy.float64'> -> time: 21.45645523071289 , size: 400.000224
        Profiled <class 'numpy.float32'> <class 'numpy.float32'> -> time: 9.684252738952637 , size: 200.000224
        Profiled <class 'numpy.bool_'> <class 'numpy.float64'> -> time: 21.941709518432617 , size: 225.000224
        Profiled <class 'numpy.bool_'> <class 'numpy.float32'> -> time: 9.715850591659546 , size: 125.000224
        Profiled <class 'numpy.int8'> <class 'numpy.float32'> -> time: 9.680383825302124 , size: 125.000224
        """


if __name__ == '__main__':
    unittest.main()
