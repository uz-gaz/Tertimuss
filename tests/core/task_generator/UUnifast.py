import unittest

from main.core.problem_specification.automatic_task_generator.implementations.UUniFast import UUniFast


class UUnifastTest(unittest.TestCase):

    def test_uunifast(self):
        u = UUniFast()
        x = u.generate(
            {
                "min_period_interval": 2,
                "max_period_interval": 12,
                "hyperperiod": 24,
                "number_of_tasks": 10,
                "utilization": 2,
                "processor_frequency": 100,
            }
        )

        print(sum([i.c / i.t for i in x]))
        assert (199 <= sum([i.c / i.t for i in x]) <= 200)
        num_wcet_zero = len([0 for i in x if i.c == 0])
        print("Number of zero execution time tasks", num_wcet_zero)

    def test_uunifast_large(self):
        u = UUniFast()
        x = u.generate(
            {
                "min_period_interval": 100000,
                "max_period_interval": 200000,
                "number_of_tasks": 10000,
                "utilization": 1.1,
                "processor_frequency": 1000,
            }
        )
        
        num_wcet_zero = len([0 for i in x if i.c == 0])

        print("Number of zero execution time tasks", num_wcet_zero)
            
        print(sum([i.c / i.t for i in x]))

        # assert (1099 < sum([i.c / i.t for i in x]) < 1101)


if __name__ == '__main__':
    unittest.main()
