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
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.tcpn_model_generator.GlobalModel import GlobalModel
from main.core.tcpn_model_generator.ThermalModelSelector import ThermalModelSelector
from main.core.tcpn_simulator.implementation.numerical_integration.TcpnSimulatorIntegrationVariableStep import \
    TcpnSimulatorIntegrationVariableStep
from main.core.tcpn_simulator.implementation.numerical_integration.TcpnSimulatorOptimizedTasksAndProcessors import \
    TcpnSimulatorOptimizedTasksAndProcessors
from main.core.tcpn_simulator.template.AbstractTcpnSimulator import AbstractTcpnSimulator
from main.core.tcpn_simulator.implementation.second_semantic.TcpnSimulatorAccurate import TcpnSimulatorAccurate
from main.core.tcpn_simulator.implementation.second_semantic.TcpnSimulatorAccurateOptimized import \
    TcpnSimulatorAccurateOptimized


class TestPetriNets(unittest.TestCase):

    def test_petri_net_advance_conf_1(self):
        pre = scipy.asarray([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 1]
        ])

        post = scipy.asarray([
            [0, 0, 1],
            [1, 0, 0],
            [0, 1, 0],
            [0, 1, 0]
        ])

        lambda_vector = scipy.asarray([1, 1, 1])

        mo = scipy.asarray([1, 0, 0, 0]).reshape((-1, 1))

        tcpn_simulator: AbstractTcpnSimulator = TcpnSimulatorAccurate(pre, post, None, lambda_vector, 1)

        for i in range(6):
            mo_next = tcpn_simulator.simulate_step(mo)
            mo = mo_next

        assert (scipy.array_equal(mo.reshape(-1), [1, 0, 0, 0]))

    def test_petri_net_advance_conf_2(self):
        pre = scipy.asarray([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [1, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 0]
        ])

        post = scipy.asarray([
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 1],
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        lambda_vector = scipy.asarray([1, 1, 1, 1])

        mo = scipy.asarray([3, 0, 0, 1, 3, 0, 0]).reshape((-1, 1))

        tcpn_simulator: AbstractTcpnSimulator = TcpnSimulatorAccurateOptimized(pre, post, lambda_vector, 1)

        for i in range(3):
            # 2 transitions for 1
            control = scipy.asarray([1, 1, 0, 1])
            tcpn_simulator.set_control(control)
            mo_next = tcpn_simulator.simulate_step(mo)
            mo = mo_next

            mo_next = tcpn_simulator.simulate_step(mo)
            mo = mo_next

            # 2 transitions for 3
            control = scipy.asarray([0, 1, 1, 1])
            tcpn_simulator.set_control(control)
            mo_next = tcpn_simulator.simulate_step(mo)
            mo = mo_next

            mo_next = tcpn_simulator.simulate_step(mo)
            mo = mo_next

        assert (scipy.array_equal(mo.reshape(-1), [0, 0, 3, 1, 0, 0, 3]))

    def test_petri_net_advance_conf_3(self):
        eta = 100

        pre = scipy.asarray([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [eta, 0, eta, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 0]
        ])

        post = scipy.asarray([
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, eta, 0, eta],
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        lambda_vector = scipy.asarray([eta, 1, eta, 1])

        mo = scipy.asarray([3, 0, 0, 1, 3, 0, 0]).reshape((-1, 1))

        tcpn_simulator: AbstractTcpnSimulator = TcpnSimulatorAccurateOptimized(pre, post, lambda_vector, 1)

        for i in range(3):
            # 2 transitions for 1
            control = scipy.asarray([1, 1, 0, 1])
            tcpn_simulator.set_control(control)
            mo_next = tcpn_simulator.simulate_step(mo)
            mo = mo_next

            mo_next = tcpn_simulator.simulate_step(mo)
            mo = mo_next

            # 2 transitions for 3
            control = scipy.asarray([0, 1, 1, 1])
            tcpn_simulator.set_control(control)
            mo_next = tcpn_simulator.simulate_step(mo)
            mo = mo_next

            mo_next = tcpn_simulator.simulate_step(mo)
            mo = mo_next

        array_to_compare = [3 - 3 * (1 / eta), 0, 3 * (1 / eta), 1, 3 - 3 * (1 / eta), 0, 3 * (1 / eta)]
        print(mo.reshape(-1), array_to_compare)

    def test_petri_net_task_processor(self):
        tasks = [PeriodicTask(2000, 4, 4, 6.4), PeriodicTask(5000, 8, 8, 8), PeriodicTask(6000, 12, 12, 9.6)]

        tasks_specification: TasksSpecification = TasksSpecification(tasks)

        core_specification = CoreGroupSpecification(MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                    EnergyConsumptionProperties(),
                                                    [150, 400, 600, 850, 1000],
                                                    [1000, 1000])

        board_specification = BoardSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400))

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01, False)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification,
                                                                        CpuSpecification(board_specification,
                                                                                         core_specification),
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification)

        pre = global_model.pre_proc_tau

        post = global_model.post_proc_tau

        lambda_vector = global_model.lambda_vector_proc_tau

        mo = global_model.mo_proc_tau

        pi = global_model.pi_proc_tau

        tcpn_simulator: AbstractTcpnSimulator = TcpnSimulatorIntegrationVariableStep(pre, post, pi, lambda_vector, 0.01)

        # control = [
        #     [1, 0, 0, 1, 0, 0],
        #     [1, 0, 0, 1, 0, 0],
        #     [1, 0, 0, 1, 0, 0],
        #     [1, 0, 0, 1, 0, 0],
        #     [0, 1, 0, 0, 0, 1],
        #     [0, 1, 0, 0, 0, 1],
        #     [0, 1, 0, 0, 0, 1],
        #     [0, 1, 0, 0, 0, 1]
        # ]

        control = 100 * [[1, 0, 0, 0, 0, 0]]

        mo_tcpn = []

        control_task_proc = scipy.ones(len(global_model.lambda_vector_proc_tau))
        m = len(core_specification.cores_frequencies)
        n = len(tasks_specification.periodic_tasks)

        for w_alloc in control:
            # Create new control vector
            new_control_processor = scipy.copy(control_task_proc)
            # Control over t_alloc
            new_control_processor[n:n + n * m] = scipy.asarray(w_alloc)
            # Control over t_exec
            new_control_processor[-n * m:] = 1

            tcpn_simulator.set_control(new_control_processor)
            mo_next = tcpn_simulator.simulate_step(mo)
            mo = mo_next
            mo_tcpn.append(mo)

        result = scipy.concatenate(mo_tcpn, axis=1)
        my_breakpoint = 1

    def test_petri_net_task_processor_one_cpu_one_task(self):
        tasks = [PeriodicTask(2000, 4, 4, 6.4)]

        tasks_specification: TasksSpecification = TasksSpecification(tasks)

        core_specification = CoreGroupSpecification(MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                    EnergyConsumptionProperties(),
                                                    [150, 400, 600, 850, 1000],
                                                    [1000])

        board_specification = BoardSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400))

        environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

        simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.01, False)

        tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
            ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

        global_specification: GlobalSpecification = GlobalSpecification(tasks_specification,
                                                                        CpuSpecification(board_specification,
                                                                                         core_specification),
                                                                        environment_specification,
                                                                        simulation_specification,
                                                                        tcpn_model_specification)

        global_model = GlobalModel(global_specification)

        pre = global_model.pre_proc_tau

        post = global_model.post_proc_tau

        lambda_vector = global_model.lambda_vector_proc_tau

        mo = global_model.mo_proc_tau

        pi = global_model.pi_proc_tau

        tcpn_simulator: AbstractTcpnSimulator = TcpnSimulatorOptimizedTasksAndProcessors(pre, post, pi, lambda_vector,
                                                                                         128, 0.01)

        # control = [
        #     [1, 0, 0, 1, 0, 0],
        #     [1, 0, 0, 1, 0, 0],
        #     [1, 0, 0, 1, 0, 0],
        #     [1, 0, 0, 1, 0, 0],
        #     [0, 1, 0, 0, 0, 1],
        #     [0, 1, 0, 0, 0, 1],
        #     [0, 1, 0, 0, 0, 1],
        #     [0, 1, 0, 0, 0, 1]
        # ]

        control = 100 * [[1]] + 100 * [[0]] + 100 * [[1]]

        mo_tcpn = []

        control_task_proc = scipy.ones(len(global_model.lambda_vector_proc_tau))
        m = len(core_specification.cores_frequencies)
        n = len(tasks_specification.periodic_tasks)

        iter_left = len(control)
        for w_alloc in control:
            print(iter_left)
            iter_left = iter_left - 1
            # Create new control vector
            new_control_processor = scipy.copy(control_task_proc)
            # Control over t_alloc
            new_control_processor[n:n + n * m] = scipy.asarray(w_alloc)
            # Control over t_exec
            new_control_processor[-n * m:] = 1

            tcpn_simulator.set_control(new_control_processor)
            mo_next = tcpn_simulator.simulate_step(mo)
            mo = mo_next
            mo_tcpn.append(mo)

        result = scipy.concatenate(mo_tcpn, axis=1)
        my_breakpoint = 1


if __name__ == '__main__':
    unittest.main()
