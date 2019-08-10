import unittest
from nodejs.bindings import node_run



class MyTestCase(unittest.TestCase):
    def test_something(self):
        #stderr, stdout = node_run('/path/to/some/file.js', '--some-argument')
        pass


if __name__ == '__main__':
    unittest.main()
