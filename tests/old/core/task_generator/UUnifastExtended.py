import unittest

import numpy

from main.core.problem_specification.automatic_task_generator.implementations.UUniFastExtended import UUniFastExtended


class UUnifastExtendedTest(unittest.TestCase):

    def test_uunifast(self):
        u = UUniFastExtended()
        x = u.generate(
            {
                "hyperperiod": 24,
                "number_of_tasks": 10,
                "utilization": 2,
                "wcet_multiple": 240,
                "processor_frequency": 3000,
            }
        )

        assert (numpy.isclose(sum([i.c / i.temperature for i in x]), 6000))
        assert (len([0 for i in x if i.c == 0]) == 0)


if __name__ == '__main__':
    unittest.main()
