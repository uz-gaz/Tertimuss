import unittest
from typing import List

import numpy

import scipy.sparse

from tertimuss.tcpn_simulator import SVSEuler
from tertimuss.tcpn_simulator import SVSRungeKutta


class TCPNSimulatorTest(unittest.TestCase):

    @staticmethod
    def _check_difference(mo_1: List[float], mo_2: List[float], error: float = 0.05) -> bool:
        return len(mo_1) == len(mo_2) and all(abs(i - j) < error for i, j in zip(mo_1, mo_2))

    def test_petri_net_rk(self):
        eta = 100

        pre = numpy.asarray([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [eta, 0, eta, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 0]
        ])

        post = numpy.asarray([
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, eta, 0, eta],
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        lambda_vector = numpy.asarray([eta, 1, eta, 1])

        mo: numpy.ndarray = numpy.asarray([3, 0, 0, 1, 3, 0, 0]).reshape((-1, 1))

        tcpn_simulator: SVSRungeKutta = SVSRungeKutta(scipy.sparse.csr_matrix(pre),
                                                      scipy.sparse.csr_matrix(post),
                                                      lambda_vector, None, True)

        for i in range(3):
            # 2 transitions for 1
            control = numpy.asarray([1, 1, 0, 1])
            tcpn_simulator.set_control(control)
            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

            # 2 transitions for 3
            control = numpy.asarray([0, 1, 1, 1])
            tcpn_simulator.set_control(control)
            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

        array_to_compare = [3 - 3 * (1 / eta), 0, 3 * (1 / eta), 1, 3 - 3 * (1 / eta), 0, 3 * (1 / eta)]

        assert self._check_difference(mo.tolist(), array_to_compare)

    def test_petri_net_euler(self):
        eta = 100

        pre = numpy.asarray([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [eta, 0, eta, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 0]
        ])

        post = numpy.asarray([
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, eta, 0, eta],
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        lambda_vector = numpy.asarray([eta, 1, eta, 1])

        mo = numpy.asarray([3, 0, 0, 1, 3, 0, 0]).reshape((-1, 1))

        tcpn_simulator: SVSEuler = SVSEuler(scipy.sparse.csr_matrix(pre),
                                            scipy.sparse.csr_matrix(post),
                                            lambda_vector, None, 64, True)

        for i in range(3):
            # 2 transitions for 1
            control = numpy.asarray([1, 1, 0, 1])
            tcpn_simulator.set_control(control)
            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

            # 2 transitions for 3
            control = numpy.asarray([0, 1, 1, 1])
            tcpn_simulator.set_control(control)
            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

            mo_next = tcpn_simulator.simulate_step(mo, 1)
            mo = mo_next

        array_to_compare = [3 - 3 * (1 / eta), 0, 3 * (1 / eta), 1, 3 - 3 * (1 / eta), 0, 3 * (1 / eta)]

        assert self._check_difference(mo.tolist(), array_to_compare)


if __name__ == '__main__':
    unittest.main()
