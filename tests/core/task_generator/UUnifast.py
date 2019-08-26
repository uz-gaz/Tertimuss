import unittest

from main.core.task_generator.implementations.UUniFast import UUniFast


class UUnifastTest(unittest.TestCase):

    def test_uunifast(self):
        u = UUniFast()
        x = u.generate(
            {
                "min_period_interval": 3.1,
                "max_period_interval": 8.5,
                "number_of_tasks": 3,
                "utilization": 1.1,
                "processor_frequency": 1000,
            }
        )

        assert (1099 < sum([i.c / i.t for i in x]) < 1101)


if __name__ == '__main__':
    unittest.main()
