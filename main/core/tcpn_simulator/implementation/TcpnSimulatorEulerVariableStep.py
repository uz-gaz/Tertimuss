import scipy
import scipy.integrate

from main.core.tcpn_simulator.template.AbstractTcpnSimulator import AbstractTcpnSimulator


class TcpnSimulatorEulerVariableStep(AbstractTcpnSimulator):
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
        self.__a = self.__calculate_a(self.__c, self.__lambda_vector, self.__pi) if self.__pi is not None else None

    def set_control(self, control: scipy.ndarray):
        """
        Apply a control action over transitions firing in the Petri net
        :param control: control
        """
        self.__control = control
        self.__a = self.__calculate_a(self.__c, self.__lambda_vector * control,
                                      self.__pi) if self.__pi is not None else None

    @staticmethod
    def __calculate_a(c: scipy.ndarray, lambda_vector: scipy.ndarray, pi: scipy.ndarray) -> scipy.ndarray:
        """
        Calculate all constant values during the simulation
        """
        return (c * lambda_vector).dot(pi)

    def simulate_step(self, mo: scipy.ndarray) -> scipy.ndarray:
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
