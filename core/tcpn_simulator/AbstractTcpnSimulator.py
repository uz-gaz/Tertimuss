import abc

import scipy


class AbstractTcpnSimulator(object, metaclass=abc.ABCMeta):
    """
    Time continuous petri net simulator
    """

    @abc.abstractmethod
    def set_pre(self, pre: scipy.ndarray):
        """
        Change pre value
        :param pre: pre
        """
        pass

    @abc.abstractmethod
    def set_post(self, post: scipy.ndarray):
        """
        Change post value
        :param post: post
        """
        pass

    @abc.abstractmethod
    def set_lambda(self, lambda_vector: scipy.ndarray):
        """
        Change lambda value
        :param lambda_vector: lambda
        """
        pass

    @abc.abstractmethod
    def set_control(self, control: scipy.ndarray):
        """
        Apply a control action over transitions firing in the Petri net
        :param control: control
        """

    @abc.abstractmethod
    def set_pi(self, pi: scipy.ndarray):
        """
        Set the PI
        :param pi: pi
        """

    @abc.abstractmethod
    def set_step(self, step: float):
        """
        Set the step of the simulation
        :param step: step
        """
        pass

    @abc.abstractmethod
    def simulate_step(self, mo: scipy.ndarray) -> scipy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :param step: step size
        :return: next marking
        """
        pass
