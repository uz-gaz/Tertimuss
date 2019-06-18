import sys
import time

import scipy

import scipy.linalg

from core.tcpn_simulator.TcpnSimulatorAccurate import TcpnSimulatorAccurate
from core.tcpn_simulator.TcpnSimulatorAccurateOptimized import TcpnSimulatorAccurateOptimized
from core.tcpn_simulator.TcpnSimulatorEuler import TcpnSimulatorEuler


def test_performance_petri_net_with_control():
    # Petri net size
    petri_net_size = 2000

    # Petri net replications
    # petri_net_replications = 1

    # Simulation steps
    simulation_steps = 100

    # Transitions to P1
    pre_p1 = scipy.asarray(petri_net_size * [1, 0, 0]).reshape((1, -1))
    post_p1 = scipy.asarray(petri_net_size * [1, 0, 0]).reshape((1, -1))

    # Other transitions
    pre = scipy.linalg.block_diag(
        *(petri_net_size * [scipy.asarray([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ])]))

    pre = scipy.concatenate([pre_p1, pre], axis=0)

    post = scipy.linalg.block_diag(
        *(petri_net_size * [scipy.asarray([
            [0, 0, 1],
            [1, 0, 0],
            [0, 1, 0],
        ])]))

    post = scipy.concatenate([post_p1, post], axis=0)

    lambda_vector = scipy.asarray(petri_net_size * [1, 1, 1])

    mo = scipy.asarray([1] + (petri_net_size * [3, 0, 0])).reshape((-1, 1))

    tcpn_simulator: TcpnSimulatorAccurateOptimized = TcpnSimulatorAccurateOptimized(pre, post, lambda_vector)

    # Array where t 3*n + 1 are disabled
    control_model_array = scipy.asarray(petri_net_size * [0, 1, 1])

    # Actual transition enabled
    actual_transition_enabled = 0

    time1 = time.time()
    for _ in range(simulation_steps):
        # Apply control action
        control = scipy.copy(control_model_array)
        control[3 * actual_transition_enabled] = 1
        tcpn_simulator.apply_control(control)

        # Simulate step
        mo = tcpn_simulator.simulate_step(mo, 1)

        # Next transition enabled
        actual_transition_enabled = (actual_transition_enabled + 1) % petri_net_size

    time2 = time.time()

    print("Time taken:", time2 - time1, "s,", "Size of pre:", sys.getsizeof(pre) / 1000000, "MB")
    print("Simulation dimensions:", 3 * petri_net_size, "transitions,", 3 * petri_net_size + 1, "places,",
          simulation_steps, "simulation steps")


def test_performance_petri_net_with_control_pi_setted():
    # Petri net size
    petri_net_size = 2000

    # Petri net replications
    # petri_net_replications = 1

    # Simulation steps
    simulation_steps = 100

    # Transitions to P1
    pre_p1 = scipy.asarray(petri_net_size * [1, 0, 0]).reshape((1, -1))
    post_p1 = scipy.asarray(petri_net_size * [1, 0, 0]).reshape((1, -1))
    pi_p1 = scipy.asarray(petri_net_size * [0, 0, 0]).reshape((1, -1))

    # Other transitions
    pre = scipy.linalg.block_diag(
        *(petri_net_size * [scipy.asarray([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ])]))

    pre = scipy.concatenate([pre_p1, pre], axis=0)

    post = scipy.linalg.block_diag(
        *(petri_net_size * [scipy.asarray([
            [0, 0, 1],
            [1, 0, 0],
            [0, 1, 0],
        ])]))

    post = scipy.concatenate([post_p1, post], axis=0)

    pi = scipy.linalg.block_diag(
        *(petri_net_size * [scipy.asarray([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ])]))

    pi = scipy.concatenate([pi_p1, pi], axis=0).transpose()

    lambda_vector = scipy.asarray(petri_net_size * [1, 1, 1])

    mo = scipy.asarray([1] + (petri_net_size * [3, 0, 0])).reshape((-1, 1))

    tcpn_simulator: TcpnSimulatorEuler = TcpnSimulatorEuler(pre, post, lambda_vector)
    tcpn_simulator.set_pi(pi)

    # Array where t 3*n + 1 are disabled
    control_model_array = scipy.asarray(petri_net_size * [0, 1, 1])

    # Actual transition enabled
    actual_transition_enabled = 0

    time1 = time.time()
    for _ in range(simulation_steps):
        # Apply control action
        control = scipy.copy(control_model_array)
        control[3 * actual_transition_enabled] = 1
        tcpn_simulator.apply_control(control)

        # Simulate step
        mo = tcpn_simulator.simulate_step(mo, 1)

        # Next transition enabled
        actual_transition_enabled = (actual_transition_enabled + 1) % petri_net_size

    time2 = time.time()

    print("Time taken:", time2 - time1, "s,", "Size of pre:", sys.getsizeof(pre) / 1000000, "MB")
    print("Simulation dimensions:", 3 * petri_net_size, "transitions,", 3 * petri_net_size + 1, "places,",
          simulation_steps, "simulation steps")


if __name__ == '__main__':
    test_performance_petri_net_with_control_pi_setted()

    """
    Performance history:
    Version 1: 16 jun, 18:05 -> Time taken: 24.094393014907837 s, Size of pre: 6.487312 MB
                                Simulation dimensions: 900 transitions, 901 places, 100 simulation steps

    Version 2 (Optimized): 17 jun, 12:39 -> Time taken: 1.0696501731872559 s, Size of pre: 6.487312 MB
                                            Simulation dimensions: 900 transitions, 901 places, 100 simulation steps

                                            Time taken: 17.84611439704895 s, Size of pre: 72.024112 MB
                                            Simulation dimensions: 3000 transitions, 3001 places, 100 simulation steps

                                            Time taken: 70.29988121986389 s, Size of pre: 288.048112 MB
                                            Simulation dimensions: 6000 transitions, 6001 places, 100 simulation steps

    Version 1 (Setted pi): 17 jun, 13:10 -> Time taken: 9.547635316848755 s, Size of pre: 72.024112 MB
                                            Simulation dimensions: 3000 transitions, 3001 places, 100 simulation steps
                                            
                                            Time taken: 44.11157035827637 s, Size of pre: 288.048112 MB
                                            Simulation dimensions: 6000 transitions, 6001 places, 100 simulation steps
                                            
    Version Euler: 18 jun, 13:05 ->         Time taken: 50.05803847312927 s, Size of pre: 144.024112 MB
                                            Simulation dimensions: 6000 transitions, 6001 places, 100 simulation steps
    """
