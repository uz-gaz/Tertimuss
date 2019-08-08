from typing import Optional

import scipy

from main.core.tcpn_simulator.template.AbstractTcpnSimulator import AbstractTcpnSimulator


class TcpnSimulatorAccurate(AbstractTcpnSimulator):
    """
    Time continuous petri net simulator optimized for the scenario where pi is invariable
    WARNING: This is only an example not used in the simulator but it may be useful if the petri net model for the
    simulation change
    """

    def __init__(self, pre: scipy.ndarray, post: scipy.ndarray, pi: Optional[scipy.ndarray],
                 lambda_vector: scipy.ndarray, step: float):
        """
        Define the Petri net
        :param pre: pre
        :param post: post
        :param lambda_vector: lambda
        """
        self.__pre = pre
        self.__post = post
        self.__lambda_vector = lambda_vector
        self.__control = scipy.ones(len(lambda_vector))
        self.__pi = pi
        self.__c = self.__post - self.__pre
        self.__step = step
        self.__calculate_constant_values()

    def set_pre(self, pre: scipy.ndarray):
        """
        Change pre value
        :param pre: pre
        """
        self.__pre = pre
        self.__c = self.__post - self.__pre

    def set_post(self, post: scipy.ndarray):
        """
        Change post value
        :param post: post
        """
        self.__post = post
        self.__c = self.__post - self.__pre

    def set_lambda(self, lambda_vector: scipy.ndarray):
        """
        Change lambda value
        :param lambda_vector: lambda
        """
        self.__lambda_vector = lambda_vector
        self.__calculate_constant_values()

    def set_control(self, control: scipy.ndarray):
        """
        Apply a control action over transitions firing in the Petri net
        :param control: control
        """
        self.__control = control
        self.__calculate_constant_values()

    def set_pi(self, pi: scipy.ndarray):
        """
        Set the PI
        :param pi: pi
        """
        self.__pi = pi

    def set_step(self, step: float):
        """
        Set the step of the simulation
        :param step: step
        """
        self.__step = step
        self.__calculate_constant_values()

    def calculate_and_set_pi(self, mo: scipy.ndarray):
        """
        Calculate the Pi for the actual marking and set it
        :param mo: mo
        """
        self.__pi = self.__calculate_pi(mo)

    def __calculate_pi(self, mo: scipy.ndarray):
        """
        Calculate pi
        :param mo: actual marking
        :return: pi
        """
        pre_transpose = self.__pre.transpose()
        pi = scipy.zeros(pre_transpose.shape)

        for i in range(len(pre_transpose)):
            places = pre_transpose[i]
            max_index = -1
            max_global = 0
            for j in range(len(places)):
                if places[j] != 0:
                    if mo[j] != 0:
                        max_interior = places[j] / mo[j]
                        if max_global < max_interior:
                            max_global = max_interior
                            max_index = j
                    else:
                        max_index = -1
                        break
            if max_index != -1:
                pi[i][max_index] = 1 / places[max_index]

        return pi

    def __calculate_constant_values(self):
        """
        Calculate all constant values during the simulation
        """
        # Max number of activations for each transition (limited by the actual control, the lambda and the step)
        self.limitation_lambda = self.__lambda_vector * self.__control * self.__step

    def simulate_step(self, mo: scipy.ndarray) -> scipy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :return: next marking
        """
        pi = self.__calculate_pi(mo) if self.__pi is None else self.__pi

        # Max number of activations for each transition (limited by the actual marking)
        limitation_marking = pi.dot(mo).reshape(-1)

        # Number of activations for each transition
        flow = scipy.minimum(self.limitation_lambda, limitation_marking).reshape((-1, 1))

        # Return the next marking
        return self.__c.dot(flow) + mo
