import unittest

import scipy

from core.tcpn_simulator.TcpnSimulator import TcpnSimulator


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

        tcpn_simulator: TcpnSimulator = TcpnSimulator(pre, post, lambda_vector)

        for i in range(6):
            mo_next = tcpn_simulator.simulate_step(mo, 1)
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

        tcpn_simulator: TcpnSimulator = TcpnSimulator(pre, post, lambda_vector)

        for i in range(3):
            # 2 transitions for 1
            control = scipy.asarray([1, 1, 0, 1])
            tcpn_simulator.apply_control(control)
            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

            # 2 transitions for 3
            control = scipy.asarray([0, 1, 1, 1])
            tcpn_simulator.apply_control(control)
            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

            mo_next = tcpn_simulator.simulate_step(mo, 1)
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

        tcpn_simulator: TcpnSimulator = TcpnSimulator(pre, post, lambda_vector)

        for i in range(3):
            # 2 transitions for 1
            control = scipy.asarray([1, 1, 0, 1])
            tcpn_simulator.apply_control(control)
            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

            # 2 transitions for 3
            control = scipy.asarray([0, 1, 1, 1])
            tcpn_simulator.apply_control(control)
            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

        array_to_compare = [3 - 3 * (1 / eta), 0, 3 * (1 / eta), 1, 3 - 3 * (1 / eta), 0, 3 * (1 / eta)]
        print(mo.reshape(-1), array_to_compare)


if __name__ == '__main__':
    unittest.main()
