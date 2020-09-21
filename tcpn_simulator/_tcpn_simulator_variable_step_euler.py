from typing import Optional

import numpy
import scipy.sparse

from ._abstract_tcpn_simulator import AbstractTCPNSimulatorVariableStep


class TCPNSimulatorVariableStepEuler(AbstractTCPNSimulatorVariableStep):
    """
    Time continuous Petri net simulator based on the Euler method
    """

    def __init__(self, pre: scipy.sparse.csr_matrix, post: scipy.sparse.csr_matrix,
                 lambda_vector: numpy.ndarray, pi: Optional[scipy.sparse.csr_matrix], number_of_steps: int,
                 constant_pi: bool = False):
        """
        Define the TCPN
        :param pre: pre matrix
        :param post: post matrix
        :param pi: pi matrix
        :param lambda_vector: lambda vector
        :param number_of_steps: number of steps in the integration
        """
        self.__lambda_vector: numpy.ndarray = lambda_vector
        self.__control: numpy.ndarray = numpy.ones(len(lambda_vector))
        self.__pi: scipy.sparse.csr_matrix = pi
        self.__pre = pre
        self.__c: scipy.sparse.csr_matrix = post - pre
        self.__number_of_steps: int = number_of_steps
        self.__constant_pi = constant_pi

    def set_control(self, control: numpy.ndarray):
        """
        Apply a control action over transitions firing in the TCPN
        :param control: control
        """
        self.__control = control

    @staticmethod
    def __calculate_a(c: scipy.sparse.csr_matrix, lambda_vector: numpy.ndarray, pi: scipy.sparse.csr_matrix,
                      fragmented_dt: float) -> scipy.sparse.csr_matrix:
        """
        Calculate a matrix
        """
        return (c.dot(scipy.sparse.diags(lambda_vector.reshape(-1)))).dot(pi) * fragmented_dt

    def simulate_step(self, mo: numpy.ndarray, dt: float) -> numpy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :param dt:  time to advance
        :return: next marking
        """
        # Real part
        pi = self.__pi if self.__pi is not None else self._calculate_pi(self.__pre, mo)

        if self.__constant_pi:
            self.__pi = pi

        a = self.__calculate_a(self.__c, self.__lambda_vector, pi, dt / self.__number_of_steps) \
            if self.__control is not None else self.__calculate_a(self.__c, self.__lambda_vector * self.__control,
                                                                  pi, dt / self.__number_of_steps)

        a_i = a + scipy.sparse.identity(a.shape[0], dtype=a.dtype)

        mo_next = mo

        for i in range(self.__number_of_steps):
            mo_next = a_i.dot(mo_next)

        return mo_next
