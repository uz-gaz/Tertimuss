import numpy

from main.core.tcpn_simulator.template.AbstractTcpnSimulator import AbstractTcpnSimulator


class TcpnSimulatorAccurateOptimized(AbstractTcpnSimulator):
    """
    Time continuous Petri net simulator optimized for the scenario where Pi is variable
    WARNING: This is only an example, it is not used in the simulator but it may be useful if the Petri net model of the
    simulation change
    """

    def __init__(self, pre: numpy.ndarray, post: numpy.ndarray, lambda_vector: numpy.ndarray, step: float):
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
        self.__c = self.__post - self.__pre
        self.__step = step
        self.__recalculate_pre_inv()
        self.__calculate_constant_values()

    def set_pre(self, pre: numpy.ndarray):
        """
        Change pre value
        :param pre: pre
        """
        self.__pre = pre
        self.__c = self.__post - self.__pre
        self.__recalculate_pre_inv()

    def set_post(self, post: numpy.ndarray):
        """
        Change post value
        :param post: post
        """
        self.__post = post
        self.__c = self.__post - self.__pre

    def set_lambda(self, lambda_vector: numpy.ndarray):
        """
        Change lambda value
        :param lambda_vector: lambda
        """
        self.__lambda_vector = lambda_vector
        self.__calculate_constant_values()

    def set_control(self, control: numpy.ndarray):
        """
        Apply a control action over transitions firing in the Petri net
        :param control: control
        """
        self.__control = control
        self.__calculate_constant_values()

    def set_pi(self, pi: numpy.ndarray):
        """
         Set the PI
         :param pi: pi
         """
        pass

    def set_step(self, step: float):
        """
         Set the step of the simulation
         :param step: step
         """
        self.__step = step
        self.__calculate_constant_values()

    def __recalculate_pre_inv(self):
        """
        Recalculate pre inv constant value
        """
        self.__pre_inv = numpy.vectorize(lambda x: numpy.nan if x == 0 else 1 / x)(self.__pre)

    def __calculate_constant_values(self):
        """
        Calculate all constant values during the simulation
        """
        # Max number of activations for each transition (limited by the actual control, the lambda and the step)
        self.__limitation_lambda = self.__lambda_vector * self.__control * self.__step

    def simulate_step(self, mo: numpy.ndarray) -> numpy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :return: next marking
        """

        # Max number of activations for each transition (limited by the actual marking
        limitation_marking = numpy.nanmin(self.__pre_inv * mo, axis=0)

        # It is only necessary if there are transitions without inputs (not the case)
        # limitation_marking = numpy.vectorize(lambda x: 0 if x == numpy.nan else x)(limitation_marking)

        # Number of activations for each transition
        flow = numpy.minimum(self.__limitation_lambda, limitation_marking).reshape((-1, 1))

        # Return the next marking
        return self.__c.dot(flow) + mo
