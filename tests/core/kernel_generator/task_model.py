from core.problem_specification.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification.TasksSpecification import TasksSpecification, PeriodicTask, AperiodicTask
import hashlib

import unittest

from core.tcpn_model_generator.tasks_model import TasksModel


class TestTaskModel(unittest.TestCase):

    def test_processor_model(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8, 8),
                                                                      PeriodicTask(3, 12, 12, 9.6)])

        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [1, 0.85, 0.75])

        task_model: TasksModel = TasksModel(tasks_specification, cpu_specification)

        # Test with hashes, the probability of collision is low
        self.assertEqual(hashlib.md5(task_model.pre_tau).hexdigest(), "f208c292b9bc6cbd37254d8e6197dc82")
        self.assertEqual(hashlib.md5(task_model.pre_alloc_tau).hexdigest(), "ef0edab73784663ec4a4ccf61e9bf793")
        self.assertEqual(hashlib.md5(task_model.post_tau).hexdigest(), "0ad2f49e1f9cab4e5552ea2c2d2d16e7")
        self.assertEqual(hashlib.md5(task_model.post_alloc_tau).hexdigest(), "4556165d7fe41c7700cbe455a5767d40")
        self.assertEqual(hashlib.md5(task_model.pi_tau).hexdigest(), "f208c292b9bc6cbd37254d8e6197dc82")
        self.assertEqual(hashlib.md5(task_model.pi_alloc_tau).hexdigest(), "4556165d7fe41c7700cbe455a5767d40")
        self.assertEqual(hashlib.md5(task_model.lambda_vector_tau).hexdigest(), "ff48ef0455bf43a3fd57abaeff011e56")
        self.assertEqual(hashlib.md5(task_model.mo_tau).hexdigest(), "3faafba237636b931721e127236abf19")

    def test_processor_model_with_aperiodic(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8, 8),
                                                                      PeriodicTask(3, 12, 12, 9.6),
                                                                      AperiodicTask(1, 2, 15, 6)
                                                                      ])

        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [1, 0.85, 0.75])

        task_model: TasksModel = TasksModel(tasks_specification, cpu_specification)

        # Test with hashes, the probability of collision is low
        self.assertEqual(hashlib.md5(task_model.pre_tau).hexdigest(), "a9d3ad03b0b10a3cc212aea221abcfcf")
        self.assertEqual(hashlib.md5(task_model.pre_alloc_tau).hexdigest(), "136b3ec3fcb3cadbbbfc348a829cc32c")
        self.assertEqual(hashlib.md5(task_model.post_tau).hexdigest(), "d5d2692e6c292713d96e07db546effeb")
        self.assertEqual(hashlib.md5(task_model.post_alloc_tau).hexdigest(), "d26937a0a615266ccd9fb199e7fb7fb9")
        self.assertEqual(hashlib.md5(task_model.pi_tau).hexdigest(), "a9d3ad03b0b10a3cc212aea221abcfcf")
        self.assertEqual(hashlib.md5(task_model.pi_alloc_tau).hexdigest(), "d26937a0a615266ccd9fb199e7fb7fb9")
        self.assertEqual(hashlib.md5(task_model.lambda_vector_tau).hexdigest(), "ff48ef0455bf43a3fd57abaeff011e56")
        self.assertEqual(hashlib.md5(task_model.mo_tau).hexdigest(), "a90715ac390f483d3300d1e237fc68ad")


if __name__ == '__main__':
    unittest.main()
