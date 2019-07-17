import unittest

from core.task_generator.UUniFast import UUniFast


class UUnifastTest(unittest.TestCase):

    def test_uunifast(self):
        u = UUniFast(3, 1.1, (3.1, 8.5), 1)
        x = u.generate()

        assert (1.09999999 < sum([i.c / i.t for i in x]) < 1.10001)


if __name__ == '__main__':
    unittest.main()
