import hashlib
import unittest

import scipy

import scipy.sparse

from core.kernel_generator.global_model import GlobalModel
from core.kernel_generator.thermal_model_selector import ThermalModelSelector
from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TCPNModelSpecification import TCPNModelSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, PeriodicTask
from core.schedulers.templates.abstract_scheduler import SchedulerResult
from core.tcpn_simulator.TcpnSimulatorAccurateOptimizedThermal import TcpnSimulatorAccurateOptimizedThermal
from output_generation.output_generator import draw_heat_matrix


class TestThermalModel(unittest.TestCase):
    def test_thermal_model(self):
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

        self.assertEqual(hashlib.md5(global_model.pre_thermal).hexdigest(), "2484d50df6ba39d26b56c7b4f1ea0a42")
        self.assertEqual(hashlib.md5(global_model.post_thermal).hexdigest(), "818291b431aa9a18e9355f20c1028cc5")
        self.assertEqual(hashlib.md5(global_model.lambda_vector_thermal).hexdigest(),
                         "3029c16803a77e61d4478823ebf6366d")
        self.assertEqual(hashlib.md5(global_model.pi_thermal).hexdigest(),
                         "9302ccafd247d2b1be53618678717d0a")
        self.assertEqual(hashlib.md5(global_model.mo_thermal).hexdigest(), "e85c93bf3266c1282bc7af64cd3aee2c")

    def test_basic_thermal_model(self):
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

        step = 0.01

        tcpn_simulator_thermal = TcpnSimulatorAccurateOptimizedThermal(global_model.pre_thermal,
                                                                       global_model.post_thermal,
                                                                       global_model.pi_thermal,
                                                                       global_model.lambda_vector_thermal,
                                                                       step / 20, 20)

        mo_thermal = global_model.mo_thermal

        def run_step(mo):
            for _ in range(20):
                mo = tcpn_simulator_thermal.simulate_step(mo)

            return mo

        mo_map = []
        times_simulated = []
        actual_time = 0
        for i in range(200):
            times_simulated.append(actual_time)
            actual_time = actual_time + step
            mo_thermal = run_step(mo_thermal)
            mo_map.append(mo_thermal)

        # mo_thermal[-(3 * 2 + 2), 0] = 15

        for i in range(200):
            mo_thermal[-1, 0] = 1  # TODO: Review it
            times_simulated.append(actual_time)
            actual_time = actual_time + step
            mo_thermal = run_step(mo_thermal)
            mo_map.append(mo_thermal)

        mo_map = scipy.concatenate(mo_map, axis=1)
        times_simulated = scipy.asarray(times_simulated)

        scheduler_simulation = SchedulerResult(mo_map, scipy.asarray([]), scipy.asarray([]), scipy.asarray([]),
                                               scipy.asarray([]), scipy.asarray([]), scipy.asarray([]),
                                               times_simulated, scipy.asarray([]), scipy.asarray([]),
                                               global_specification.simulation_specification.dt)

        draw_heat_matrix(global_specification, global_model, scheduler_simulation)


if __name__ == '__main__':
    unittest.main()
