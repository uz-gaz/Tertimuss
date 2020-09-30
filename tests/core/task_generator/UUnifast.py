import random
import unittest

from main.core.problem_specification.automatic_task_generator.implementations.UUniFast import UUniFast
from main.core.problem_specification.automatic_task_generator.implementations.UUniFastCycles import UUniFastCycles
from main.core.problem_specification.automatic_task_generator.implementations.UUniFastDiscardCycles import \
    UUniFastDiscardCycles


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

    def test_check_unifast_run(self):

        def task_set_creator() -> bool:
            number_of_tasks = 16
            number_of_cpus = 4

            u = UUniFastDiscardCycles()
            x = u.generate(
                {
                    "min_period_interval": 1,
                    "max_period_interval": 1,
                    "number_of_tasks": number_of_tasks,
                    "utilization": number_of_cpus,
                    "processor_frequency": 1000
                }
            )

            for i in range(len(x)):
                multiplier = random.choice([1, 2, 4, 5, 8, 10, 20, 40])  # randrange(1, 9)
                x[i].d = x[i].d * multiplier
                x[i].t = x[i].t * multiplier
                x[i].c = x[i].c * multiplier

            max_period = 40

            max_cycles = round(1000 * max_period)

            total_cycles = [i.c * round(max_period / i.d) for i in x]

            task_utilization_excess = any([i > max_cycles for i in total_cycles])

            total_utilized_cycles = sum(total_cycles)

            if task_utilization_excess:
                print("Excess of utilization of task in task-set")
                return False
            elif total_utilized_cycles < max_cycles * number_of_cpus:
                print("Infra-utilized task-set")
                return False
            elif total_utilized_cycles > max_cycles * number_of_cpus:
                print("Excess of utilization in task-set")
                return False
            else:
                return True

        for _ in range(2000):
            assert (task_set_creator())


if __name__ == '__main__':
    unittest.main()
