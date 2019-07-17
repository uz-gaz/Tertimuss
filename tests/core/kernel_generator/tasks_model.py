import hashlib
import unittest

from core.tcpn_model_generator.tasks_model import TasksModel, generate_tasks_model
from core.problem_specification.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification.TasksSpecification import TasksSpecification, PeriodicTask


class TestTasksModel(unittest.TestCase):

    def test_basic_task_model(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8),
                                                                      PeriodicTask(3, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=2, p=0.2, c_p=1.2, k=0.1),
                                                               MaterialCuboid(x=10, y=10, z=2, p=0.2, c_p=1.2, k=0.1),
                                                               2, 1)

        tasks_model: TasksModel = generate_tasks_model(tasks_specification, cpu_specification)

        # Test with hashes, the probability of collision is low
        self.assertEqual(hashlib.md5(tasks_model.m_tau_o).hexdigest(), "d6df1351649854642f6615ccab72f3e1")
        self.assertEqual(hashlib.md5(tasks_model.a_tau).hexdigest(), "487ffd82f62947b52b176733ac22124e")
        self.assertEqual(hashlib.md5(tasks_model.c_tau_alloc).hexdigest(), "d36cc42f5ae552e4bd3c94d79de1f59f")
        self.assertEqual(hashlib.md5(tasks_model.c_tau).hexdigest(), "ba742c7877a673a26746b0521976d5c7")
        self.assertEqual(hashlib.md5(tasks_model.lambda_tau).hexdigest(), "b4ad8dc827b759621cb998cbddb4714f")
        self.assertEqual(hashlib.md5(tasks_model.pi_tau).hexdigest(), "94530d337e66826f051de77dabc9b3c3")


if __name__ == '__main__':
    unittest.main()
