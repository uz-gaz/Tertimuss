from typing import Optional

import numpy
import scipy.integrate

from .AbstractTcpnSimulator import AbstractTcpnSimulator


class TcpnSimulatorIntegrationVariableStep(AbstractTcpnSimulator):
    """
    Time continuous Petri net simulator based on the Runge-Kutta formula
    WARNING: This is only an example, it is not used in the simulator but it may be useful if the Petri net model of the
    simulation change
    """

    def __init__(self, pre: numpy.ndarray, post: numpy.ndarray, pi: Optional[numpy.ndarray],
                 lambda_vector: numpy.ndarray, dt: float):
        """
        Define the Petri net
        :param pre: pre
        :param post: post
        :param lambda_vector: lambda
        """
        self.__pre = pre
        self.__post = post
        self.__lambda_vector = lambda_vector
        self.__control = numpy.ones(len(lambda_vector))
        self.__pi = pi
        self.__c = self.__post - self.__pre
        self.__dt = dt
        self.__a = self.__calculate_a(self.__c, self.__lambda_vector, self.__pi) if self.__pi is not None else None

    def set_control(self, control: numpy.ndarray):
        """
        Apply a control action over transitions firing in the Petri net
        :param control: control
        """
        self.__control = control
        self.__a = self.__calculate_a(self.__c, self.__lambda_vector * control,
                                      self.__pi) if self.__pi is not None else None

    @staticmethod
    def __calculate_a(c: numpy.ndarray, lambda_vector: numpy.ndarray, pi: numpy.ndarray) -> numpy.ndarray:
        """
        Calculate all constant values during the simulation
        """
        return (c * lambda_vector).dot(pi)

    def simulate_step(self, mo: numpy.ndarray) -> numpy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :return: next marking
        """
        a = self.__a if self.__a is not None else self.__calculate_a(self.__c, self.__lambda_vector * self.__control,
                                                                     self._calculate_pi(self.__pre, mo))

        res = scipy.integrate.solve_ivp(lambda t, m: a.dot(m.reshape(-1, 1)).reshape(-1), [0, self.__dt],
                                        mo.reshape(-1),
                                        dense_output=True)

        return (res.y[:, -1]).reshape(-1, 1)
