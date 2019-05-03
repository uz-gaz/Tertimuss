import unittest

from core.task_generator.UUniFast import UUniFast


class UUnifastTest(unittest.TestCase):

    def test_uunifast(self):
        u = UUniFast(3, 1.1, (3.1, 8.5), 1)
        x = u.generate()
        print("Tasks generated with UUniFast:")
        for i in x:
            print("c:", i.c, ", t:", i.t, ", e:", i.e)


if __name__ == '__main__':
    unittest.main()
