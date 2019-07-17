from core.tcpn_model_generator.processor_model import ProcessorModel, generate_processor_model
from core.problem_specification.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification.TasksSpecification import TasksSpecification, PeriodicTask
import hashlib

import unittest


class TestProcessorModel(unittest.TestCase):

    def test_basic_processor_model(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8),
                                                                      PeriodicTask(3, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=2, p=0.2, c_p=1.2, k=0.1),
                                                               MaterialCuboid(x=10, y=10, z=2, p=0.2, c_p=1.2, k=0.1),
                                                               2, 1)

        processor_model: ProcessorModel = generate_processor_model(tasks_specification, cpu_specification)

        # Test with hashes, the probability of collision is low
        self.assertEqual(hashlib.md5(processor_model.m_proc_o).hexdigest(), "a7a41fb2b42bf12daa87fa51608c0745")
        self.assertEqual(hashlib.md5(processor_model.a_proc).hexdigest(), "c3839e30f3821b282cd294b406ebd94b")
        self.assertEqual(hashlib.md5(processor_model.s_exec).hexdigest(), "937fcb903b3f54526cb2df22c146ee5f")
        self.assertEqual(hashlib.md5(processor_model.s_busy).hexdigest(), "f960f7492210a8301e8d24ca2511f4b2")
        self.assertEqual(hashlib.md5(processor_model.c_proc_alloc).hexdigest(), "8b837e81c66f1fab4340e27f8050a01e")
        self.assertEqual(hashlib.md5(processor_model.c_proc).hexdigest(), "308c7dddbd20417cea1ef85baed3645d")
        self.assertEqual(hashlib.md5(processor_model.lambda_proc).hexdigest(), "9faf6c0363cf07f6be0a298dad5d5492")
        self.assertEqual(hashlib.md5(processor_model.pi_proc).hexdigest(), "33c3823e5d925582a78b185884fbdc5b")


if __name__ == '__main__':
    unittest.main()
