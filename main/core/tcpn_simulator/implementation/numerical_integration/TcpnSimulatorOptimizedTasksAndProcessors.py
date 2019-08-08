import scipy

from main.core.tcpn_simulator.template.AbstractTcpnSimulator import AbstractTcpnSimulator


class TcpnSimulatorOptimizedTasksAndProcessors(AbstractTcpnSimulator):
    """
    Time continuous petri net simulator based on the euler method
    WARNING: This is only an example not used in the simulator but it may be useful if the petri net model for the
    simulation change
    """

    def __init__(self, pre: scipy.ndarray, post: scipy.ndarray, pi: scipy.ndarray, lambda_vector: scipy.ndarray,
                 number_of_steps: int, dt: float):
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
        self.__dt = dt
        self.__number_of_steps = number_of_steps

        a = self.__calculate_a(self.__c, self.__lambda_vector, self.__pi, self.__dt / self.__number_of_steps)

        self.__a_multi_step: scipy.ndarray = scipy.linalg.fractional_matrix_power(
            a + scipy.identity(a.shape[0]), self.__number_of_steps)

    def set_control(self, control: scipy.ndarray):
        """
        Apply a control action over transitions firing in the Petri net
        :param control: control
        """
        self.__control = control
        a = self.__calculate_a(self.__c, self.__lambda_vector * control, self.__pi, self.__dt / self.__number_of_steps)
        self.__a_multi_step: scipy.ndarray = scipy.linalg.fractional_matrix_power(
            a + scipy.identity(a.shape[0]), self.__number_of_steps)

    @staticmethod
    def __calculate_a(c: scipy.ndarray, lambda_vector: scipy.ndarray, pi: scipy.ndarray,
                      fragmented_dt: float) -> scipy.ndarray:
        """
        Calculate all constant values during the simulation
        """
        return (c * lambda_vector).dot(pi) * fragmented_dt

    def simulate_step(self, mo: scipy.ndarray) -> scipy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :return: next marking
        """
        return self.__a_multi_step.dot(mo)
