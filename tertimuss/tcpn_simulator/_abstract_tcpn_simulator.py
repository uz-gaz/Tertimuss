import abc

import numpy

import scipy.sparse


class AbstractTCPNSimulator(object, metaclass=abc.ABCMeta):
    """
    Time continuous Petri net simulator
    """

    @abc.abstractmethod
    def set_control(self, control: numpy.ndarray):
        """
        Apply a control action over transitions firing in the Petri net

        :param control: control
        """
        pass

    @staticmethod
    def _calculate_pi(pre: scipy.sparse.csr_matrix, mo: numpy.ndarray) -> scipy.sparse.csr_matrix:
        """
        Calculate pi

        :param mo: actual marking
        :return: pi
        """
        pi = scipy.sparse.lil_matrix((pre.shape[1], pre.shape[0]), dtype=pre.dtype)

        transitions_number = pre.shape[1]
        places_number = pre.shape[0]

        for i in range(transitions_number):
            max_index = -1
            max_global = 0
            for j in range(places_number):
                if pre[j, i] != 0:
                    if mo[j] != 0:
                        max_interior = pre[j, i] / mo[j]
                        if max_global < max_interior:
                            max_global = max_interior
                            max_index = j
                    else:
                        max_index = -1
                        break
            if max_index != -1:
                pi[i, max_index] = 1 / pre[max_index, i]

        return pi.tocsr()


class AbstractTCPNSimulatorFixedStep(AbstractTCPNSimulator, metaclass=abc.ABCMeta):
    """
    Time continuous Petri net simulator fixed step
    """

    @abc.abstractmethod
    def simulate_step(self, mo: numpy.ndarray) -> numpy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :return: next marking
        """
        pass


class AbstractTCPNSimulatorVariableStep(AbstractTCPNSimulator, metaclass=abc.ABCMeta):
    """
    Time continuous Petri net simulator fixed step
    """

    @abc.abstractmethod
    def simulate_step(self, mo: numpy.ndarray, dt: float) -> numpy.ndarray:
        """
        Simulate one step

        :param mo:  actual marking
        :param dt: time to advance
        :return: next marking
        """
        pass
