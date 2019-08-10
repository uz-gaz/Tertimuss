import unittest
import subprocess



class MyTestCase(unittest.TestCase):
    def test_something(self):
        input_path = "../../../tests/cli/input-example-thermal-aperiodics-energy.json"
        subprocess.call("node", "test_node.js")
        #stderr, stdout = node_run('test_node.js')
        pass


if __name__ == '__main__':
    unittest.main()
