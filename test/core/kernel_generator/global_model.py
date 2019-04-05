import hashlib
import unittest

from core.kernel_generator.global_model import GlobalModel, generate_global_model
from core.kernel_generator.processor_model import ProcessorModel, generate_processor_model
from core.kernel_generator.tasks_model import generate_tasks_model, TasksModel
from core.kernel_generator.thermal_model import ThermalModel, generate_thermal_model
from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, Task


class TestGlobalModel(unittest.TestCase):

    def test_basic_global_model(self):
        tasks_specification: TasksSpecification = TasksSpecification([Task(2, 4, 6.4),
                                                                      Task(3, 8, 8),
                                                                      Task(3, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1)

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        processor_model: ProcessorModel = generate_processor_model(tasks_specification, cpu_specification)

        tasks_model: TasksModel = generate_tasks_model(tasks_specification, cpu_specification)

        thermal_model: ThermalModel = generate_thermal_model(tasks_specification, cpu_specification,
                                                             environment_specification,
                                                             simulation_specification)

        global_model, mo = generate_global_model(tasks_model, processor_model, thermal_model,
                                                 environment_specification)

        self.assertEqual(hashlib.md5(global_model.a).hexdigest(), "322bccabcb5438b447e9c595f938103a")
        self.assertEqual(hashlib.md5(mo).hexdigest(), "dfa9268c3a1c4479f8aff825d729cf59")
        self.assertEqual(hashlib.md5(global_model.b).hexdigest(), "d8609949db9452878b94854aabf0be29")
        self.assertEqual(hashlib.md5(global_model.bp).hexdigest(), "631e354953429412a9177770b8eb5775")
        self.assertEqual(hashlib.md5(global_model.s).hexdigest(), "e9106256fc7de60d33335b42e4490e34")
        self.assertEqual(hashlib.md5(global_model.s_thermal).hexdigest(), "102c87829dcb6064a59138c568224763")


if __name__ == '__main__':
    unittest.main()
