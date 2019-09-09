import time
import unittest

import scipy

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.cpu_specification.BoardSpecification import BoardSpecification
from main.core.problem_specification.cpu_specification.CoreGroupSpecification import CoreGroupSpecification
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.cpu_specification.EnergyConsumptionProperties import EnergyConsumptionProperties
from main.core.problem_specification.cpu_specification.MaterialCuboid import MaterialCuboid
from main.core.problem_specification.environment_specification.EnvironmentSpecification import EnvironmentSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.simulation_specification.TCPNModelSpecification import TCPNModelSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.task_generator.implementations.UUniFast import UUniFast
from main.core.tcpn_model_generator.GlobalModel import GlobalModel
from main.core.tcpn_model_generator.ThermalModelSelector import ThermalModelSelector
from main.core.tcpn_simulator.implementation.numerical_integration.TcpnSimulatorOptimizedTasksAndProcessors import \
    TcpnSimulatorOptimizedTasksAndProcessors
from main.core.tcpn_simulator.implementation.numerical_integration.TcpnSimulatorOptimizedTasksAndProcessorsIterative import \
    TcpnSimulatorOptimizedTasksAndProcessorsIterative
from main.core.tcpn_simulator.template import AbstractTcpnSimulator


class TasksProcessorsPerformanceTest(unittest.TestCase):
    @staticmethod
    def __specification_and_creation_of_the_model() -> [GlobalModel, float, int, int, int]:
        """
        Generate global model
        :return: global model, step, simulations each step, number of steps
        """
        # Simulation parameters
        dt = 0.01
        dt_fragmentation = 64
        number_of_control_changes = 10
        simulation_steps_each_control = 200
        number_of_tasks = 10000

        # Problem specification
        u = UUniFast()
        tasks = u.generate(
            {
                "min_period_interval": 100000,
                "max_period_interval": 200000,
                "number_of_tasks": number_of_tasks,
                "utilization": 1.1,
                "processor_frequency": 1000000,
            }
        )

        # tasks = [PeriodicTask(2000000, 4, 4, 6.4), PeriodicTask(5000000, 8, 8, 8), PeriodicTask(6000000, 12, 12, 9.6)]

        tasks_specification: TasksSpecification = TasksSpecification(tasks)

        core_specification = CoreGroupSpecification(MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                    EnergyConsumptionProperties(),
                                                    [150000, 400000, 600000, 850000, 1000000],
                                                    [1000000, 1000000])

        board_specification = BoardSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400))

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01, True)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification,
                                                                        CpuSpecification(board_specification,
                                                                                         core_specification),
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        # Creation of TCPN model
        global_model = GlobalModel(global_specification)

        return global_model, dt, dt_fragmentation, number_of_control_changes, simulation_steps_each_control

    def test_state_exponential_performance(self):
        """
        Simulation of execution with state equation multi step
        """
        print("Simulation of execution with state equation multi step")

        global_model, dt, dt_fragmentation, number_of_control_changes, simulation_steps_each_control = \
            self.__specification_and_creation_of_the_model()

        # TCPN simulator creation
        time_start = time.time()

        pi = global_model.pi_proc_tau
        pre = global_model.pre_proc_tau
        post = global_model.post_proc_tau
        lambda_vector = global_model.lambda_vector_proc_tau
        mo = global_model.mo_proc_tau

        tcpn_simulator: AbstractTcpnSimulator = TcpnSimulatorOptimizedTasksAndProcessors(pre, post, pi, lambda_vector,
                                                                                         dt_fragmentation, dt)

        print("Time taken creation of the TCPN solver:", time.time() - time_start)

        del global_model

        time_start = time.time()

        control_to_apply = scipy.ones(lambda_vector.shape)

        # Simulation of steps
        for i in range(number_of_control_changes):
            tcpn_simulator.set_control(control_to_apply)
            for j in range(simulation_steps_each_control):
                print(i * simulation_steps_each_control + j, "/",
                      number_of_control_changes * simulation_steps_each_control)
                mo_next = tcpn_simulator.simulate_step(mo)

        print("Time taken simulating", simulation_steps_each_control * number_of_control_changes, "steps:",
              time.time() - time_start)

        """
        Results
        400 tasks ->
            Time taken creation of the TCPN solver: 5.273777008056641
            Time taken simulating 2000 steps: 67.85808372497559
            
        1000 tasks -> 
            Time taken creation of the TCPN solver: 75.6886293888092
            Time taken simulating 2000 steps: 842.0370965003967
        """

    def test_iterative_performance(self):
        """
        Simulation of execution with iterative solution
        """
        print("Simulation of execution with iterative solution")

        global_model, dt, dt_fragmentation, number_of_control_changes, simulation_steps_each_control = \
            self.__specification_and_creation_of_the_model()

        # TCPN simulator creation
        time_start = time.time()

        pi = global_model.pi_proc_tau
        pre = global_model.pre_proc_tau
        post = global_model.post_proc_tau
        lambda_vector = global_model.lambda_vector_proc_tau
        mo = global_model.mo_proc_tau

        tcpn_simulator: AbstractTcpnSimulator = TcpnSimulatorOptimizedTasksAndProcessorsIterative(pre, post, pi,
                                                                                                  lambda_vector,
                                                                                                  dt_fragmentation, dt)

        print("Time taken creation of the TCPN solver:", time.time() - time_start)

        del global_model

        time_start = time.time()

        control_to_apply = scipy.ones(lambda_vector.shape)

        # Simulation of steps
        for i in range(number_of_control_changes):
            tcpn_simulator.set_control(control_to_apply)
            for j in range(simulation_steps_each_control):
                print(i * simulation_steps_each_control + j, "/",
                      number_of_control_changes * simulation_steps_each_control)
                mo_next = tcpn_simulator.simulate_step(mo)

        print("Time taken simulating", simulation_steps_each_control * number_of_control_changes, "steps:",
              time.time() - time_start)

        """
        Results
        400 tasks ->
            Time taken creation of the TCPN solver: 0.0035636425018310547
            Time taken simulating 2000 steps: 4.673924684524536
    
        1000 tasks -> 
            Time taken creation of the TCPN solver: 0.0035636425018310547
            Time taken simulating 2000 steps: 12.837023973464966
        
        10000 tasks -> 
            Time taken creation of the TCPN solver: 0.05525612831115723
            Time taken simulating 2000 steps: 62.246376514434814
        """


if __name__ == '__main__':
    unittest.main()
