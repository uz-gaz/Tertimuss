import hashlib
import unittest

from main.core.tcpn_model_generator.global_model import GlobalModel
from main.core.tcpn_model_generator.processor_model import ProcessorModel
from main.core.tcpn_model_generator.thermal_model_selector import ThermalModelSelector
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.cpu_specification.MaterialCuboid import MaterialCuboid
from main.core.problem_specification.environment_specification.EnvironmentSpecification import EnvironmentSpecification
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.simulation_specification.TCPNModelSpecification import TCPNModelSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask


class TestThermalModel(unittest.TestCase):

    def test_thermal_model(self):
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8, 8),
                                                                      PeriodicTask(3, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [1, 0.85, 0.75])

        processor_model: ProcessorModel = ProcessorModel(tasks_specification, cpu_specification)

        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(3, 8, 8, 8),
                                                                      PeriodicTask(3, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [1, 0.85, 0.75])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification, True)

        self.assertEqual(hashlib.md5(global_model.pre_thermal.toarray()).hexdigest(),
                         "44cc96b0f85c4c842ff0068f2493108c")
        self.assertEqual(hashlib.md5(global_model.post_thermal.toarray()).hexdigest(),
                         "3dfda63b6057a6963f8920af2736666f")
        self.assertEqual(hashlib.md5(global_model.lambda_vector_thermal).hexdigest(),
                         "3029c16803a77e61d4478823ebf6366d")
        self.assertEqual(hashlib.md5(global_model.pi_thermal.toarray()).hexdigest(),
                         "ecd7739a36bedc39a1f834b0b63051c9")
        self.assertEqual(hashlib.md5(global_model.mo_thermal).hexdigest(),
                         "e85c93bf3266c1282bc7af64cd3aee2c")


if __name__ == '__main__':
    unittest.main()
