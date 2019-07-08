from typing import Optional

import scipy
import scipy.linalg


class TcpnSimulatorAccurateOptimizedThermal(object):
    """
    Time continuous petri net simulator optimized to simulate thermal
    """

    def __init__(self, pre: scipy.ndarray, post: scipy.ndarray, pi: scipy.ndarray,
                 lambda_vector: scipy.ndarray, step: float, multi_step_number: Optional[int]):
        """
        Define the Petri net
        :param pre: pre
        :param post: post
        :param lambda_vector: lambda
        """
        self.__pi = pi
        self.__c = post - pre
        self.__pre = pre
        self.__lambda = lambda_vector
        self.__step = step
        self.__a = (self.__c * self.__lambda).dot(self.__pi) * self.__step
        self.__a_multi_step = scipy.linalg.fractional_matrix_power(self.__a + scipy.identity(len(self.__a)),
                                                                   multi_step_number) if multi_step_number \
                                                                                         is not None else None

    def set_post_and_lambda(self, post: scipy.ndarray, lambda_vector: scipy.ndarray):
        """
        Change petri net post and lambda
        """
        self.__c = post - self.__pre
        self.__lambda = lambda_vector
        self.__a = (self.__c * self.__lambda).dot(self.__pi) * self.__step

    def get_post(self):
        """
        Get post matrix
        :return:
        """
        return self.__c + self.__pre

    def get_lambda(self):
        """
        Get lambda vector
        :return:
        """
        return self.__lambda

    def simulate_step(self, mo: scipy.ndarray) -> scipy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :return: next marking
        """
        return self.__a.dot(mo) + mo

    def simulate_multi_step(self, mo: scipy.ndarray) -> scipy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :return: next marking
        """
        return self.__a_multi_step.dot(mo)
