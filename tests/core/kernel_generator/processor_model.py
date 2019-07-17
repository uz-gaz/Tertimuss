from core.tcpn_model_generator.processor_model import ProcessorModel
from core.problem_specification.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification.TasksSpecification import TasksSpecification, PeriodicTask, AperiodicTask
import hashlib

import unittest


class TestProcessorModel(unittest.TestCase):

    def test_processor_model(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8, 8),
                                                                      PeriodicTask(3, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [1, 0.85, 0.75])

        processor_model: ProcessorModel = ProcessorModel(tasks_specification, cpu_specification)

        # Test with hashes, the probability of collision is low
        self.assertEqual(hashlib.md5(processor_model.pre_alloc_proc).hexdigest(), "a469c3e9e86743f83d8b071e57a0f7da")
        self.assertEqual(hashlib.md5(processor_model.pre_exec_proc).hexdigest(), "8b837e81c66f1fab4340e27f8050a01e")
        self.assertEqual(hashlib.md5(processor_model.post_alloc_proc).hexdigest(), "8b837e81c66f1fab4340e27f8050a01e")
        self.assertEqual(hashlib.md5(processor_model.post_exec_proc).hexdigest(), "46c22e8437f7f577b69bbd2a33c32a95")
        self.assertEqual(hashlib.md5(processor_model.pi_alloc_proc).hexdigest(), "a469c3e9e86743f83d8b071e57a0f7da")
        self.assertEqual(hashlib.md5(processor_model.pi_exec_proc).hexdigest(), "8b837e81c66f1fab4340e27f8050a01e")
        self.assertEqual(hashlib.md5(processor_model.lambda_vector_alloc_proc).hexdigest(), "1c507ed6c044af516be945b78605f1d2")
        self.assertEqual(hashlib.md5(processor_model.lambda_vector_exec_proc).hexdigest(), "1c507ed6c044af516be945b78605f1d2")
        self.assertEqual(hashlib.md5(processor_model.mo_proc).hexdigest(), "a7a41fb2b42bf12daa87fa51608c0745")

    def test_processor_model_with_aperiodic(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8, 8),
                                                                      PeriodicTask(3, 12, 12, 9.6),
                                                                      AperiodicTask(1, 2, 15, 6)
                                                                      ])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [1, 0.85, 0.75])

        processor_model: ProcessorModel = ProcessorModel(tasks_specification, cpu_specification)

        # Test with hashes, the probability of collision is low
        self.assertEqual(hashlib.md5(processor_model.pre_alloc_proc).hexdigest(), "d5d28475c92743e3808fbfbd5331c7f9")
        self.assertEqual(hashlib.md5(processor_model.pre_exec_proc).hexdigest(), "a5bf2ce6d5aeb4d51f91279819c19491")
        self.assertEqual(hashlib.md5(processor_model.post_alloc_proc).hexdigest(), "a5bf2ce6d5aeb4d51f91279819c19491")
        self.assertEqual(hashlib.md5(processor_model.post_exec_proc).hexdigest(), "1f4dd317f6f0f9eb6cf40875e4407d4e")
        self.assertEqual(hashlib.md5(processor_model.pi_alloc_proc).hexdigest(), "d5d28475c92743e3808fbfbd5331c7f9")
        self.assertEqual(hashlib.md5(processor_model.pi_exec_proc).hexdigest(), "a5bf2ce6d5aeb4d51f91279819c19491")
        self.assertEqual(hashlib.md5(processor_model.lambda_vector_alloc_proc).hexdigest(), "c0e6ed96270c7f71a482d11ec03d4031")
        self.assertEqual(hashlib.md5(processor_model.lambda_vector_exec_proc).hexdigest(), "c0e6ed96270c7f71a482d11ec03d4031")
        self.assertEqual(hashlib.md5(processor_model.mo_proc).hexdigest(), "0a166c2be28b51f04fdaa8f8ef20dcca")


if __name__ == '__main__':
    unittest.main()
