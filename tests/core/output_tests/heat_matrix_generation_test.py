import sys
import time
import unittest

import scipy

from core.kernel_generator.global_model import GlobalModel
from core.kernel_generator.thermal_model_selector import ThermalModelSelector
from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TCPNModelSpecification import TCPNModelSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, PeriodicTask
from core.tcpn_simulator.TcpnSimulatorAccurateOptimizedThermal import TcpnSimulatorAccurateOptimizedThermal


class HeatMatrixGeneration(unittest.TestCase):
    def test_heat_matrix_generation_and_execution_performance(self):
        # Problem specification
        tasks_specification: TasksSpecification = TasksSpecification([PeriodicTask(2, 4, 4, 6.4),
                                                                      PeriodicTask(5, 8, 8, 8),
                                                                      PeriodicTask(6, 12, 12, 9.6)])
        cpu_specification: CpuSpecification = CpuSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400),
                                                               MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                               2, 1000, [1, 1], [0.15, 0.4, 0.6, 0.85, 1])

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        # simulation_specification: SimulationSpecification = SimulationSpecification(0.75, 0.01)
        simulation_specification: SimulationSpecification = SimulationSpecification(1, 0.01)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification, cpu_specification,
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        # Creation of TCPN model
        time_1 = time.time()
        global_model = GlobalModel(global_specification, True)
        mo = global_model.mo_thermal
        print("Size of pre and post (each one):", sys.getsizeof(global_model.pre_thermal) / (1024 ** 3), "GB")
        non_zeros_pre = scipy.count_nonzero(global_model.pre_thermal)
        non_zeros_post = scipy.count_nonzero(global_model.post_thermal)
        places_matrix_pre = global_model.pre_thermal.shape[0] * global_model.pre_thermal.shape[1]

        print("Density of pre:", non_zeros_pre / places_matrix_pre)
        print("Density of post:", non_zeros_post / places_matrix_pre)

        time_2 = time.time()
        print("Time taken creation of the model:", time_2 - time_1)

        # Creation of tcpn simulator instance
        tcpn_simulator = TcpnSimulatorAccurateOptimizedThermal(global_model.pre_thermal,
                                                               global_model.post_thermal,
                                                               global_model.pi_thermal,
                                                               global_model.lambda_vector_thermal,
                                                               simulation_specification.dt /
                                                               simulation_specification.dt_fragmentation_thermal,
                                                               simulation_specification.dt_fragmentation_thermal)
        del global_model
        a_multi_step = tcpn_simulator.get_a_multi_step()
        print("Size of a multi step:", sys.getsizeof(a_multi_step) / (1024 ** 3), "GB")
        non_zeros_a = scipy.count_nonzero(a_multi_step)
        places_matrix_a = a_multi_step.shape[0] * a_multi_step.shape[1]
        print("Density of a:", non_zeros_a / places_matrix_a)
        del a_multi_step
        time_3 = time.time()
        print("Time taken creation of the TCPN solver:", time_3 - time_2)

        # Simulation of 10 steps
        for _ in range(10):
            mo = tcpn_simulator.simulate_multi_step(mo)

        time_4 = time.time()
        print("Time taken in 10 iterations:", time_4 - time_3)

        """
        Problem with step = 1
        Size of pre and post (each one): 0.2749609798192978 GB
        Density of pre: 0.00036927621861152144
        Density of post: 0.00039095371897028406
        Time taken creation of the model: 4.430338144302368
        Size of a multi step: 0.054637178778648376 GB
        Density of a: 0.9970468811705129
        Time taken creation of the TCPN solver: 16.62180233001709
        Time taken in 10 iterations: 0.08708691596984863
        """


if __name__ == '__main__':
    unittest.main()
