import unittest

from core.task_generator.UUniFast import UUniFast


class UUnifastTest(unittest.TestCase):

    def test_uunifast(self):
        u = UUniFast(1, 1.1, (3.1, 8.5), 1)
        u.generate()


if __name__ == '__main__':
    unittest.main()
