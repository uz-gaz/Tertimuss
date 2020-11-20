import numpy
import scipy.sparse

from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification


class ProcessorModel(object):
    """
    Create the TCPN that represents the processor model
    """

    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                 simulation_specification: SimulationSpecification):
        n = len(tasks_specification.periodic_tasks) + len(tasks_specification.aperiodic_tasks)
        m = len(cpu_specification.cores_specification.operating_frequencies)

        # Transition rate (n)
        eta = 100

        # Total of places of the TCPN processor module
        p = m * (2 * n + 1)  # m processors*(n busy places, n exec places, 1 idle place)

        # Total of transitions
        t_alloc = n * m  # m processors * (n transitions alloc)
        t_exec = n * m  # m processors * (n transition exec)

        # Model marking
        mo = numpy.zeros((p, 1))

        # Model for alloc transitions
        pre_alloc = scipy.sparse.lil_matrix((p, t_alloc), dtype=simulation_specification.type_precision)
        post_alloc = scipy.sparse.lil_matrix((p, t_alloc), dtype=simulation_specification.type_precision)
        pi_alloc = scipy.sparse.lil_matrix((p, t_alloc), dtype=simulation_specification.type_precision)
        lambda_vector_alloc = numpy.zeros(t_alloc)

        # Model for exec transitions
        pre_exec = scipy.sparse.lil_matrix((p, t_exec), dtype=simulation_specification.type_precision)
        post_exec = scipy.sparse.lil_matrix((p, t_exec), dtype=simulation_specification.type_precision)
        pi_exec = scipy.sparse.lil_matrix((p, t_exec), dtype=simulation_specification.type_precision)
        lambda_vector_exec = numpy.zeros(t_exec)

        # Construction of the model
        for k in range(m):
            # f = cpu_specification.clock_relative_frequencies[k]

            i = (2 * n + 1) * k

            # Construction of matrix Post and Pre for busy and exec places (connections to transitions alloc and exec)
            pre_exec[i:i + n, k * n: k * n + n] = scipy.sparse.identity(n,
                                                                        dtype=simulation_specification.type_precision,
                                                                        format="lil")  # Arcs going from p_busy to t_exec

            post_alloc[i:i + n, k * n:k * n + n] = scipy.sparse.identity(n,
                                                                         dtype=simulation_specification.type_precision,
                                                                         format="lil")  # Arcs going from t_alloc to p_busy
            post_exec[i + n:i + 2 * n, k * n:k * n + n] = scipy.sparse.identity(n,
                                                                                dtype=simulation_specification.type_precision,
                                                                                format="lil")  # Arcs going from t_exec to p_exec

            pi_exec[i:i + n, k * n: k * n + n] = scipy.sparse.identity(n, dtype=simulation_specification.type_precision,
                                                                       format="lil")

            # Construction of matrix Post and Pre for idle place (connections to transitions alloc and exec)
            pre_alloc[i + 2 * n, k * n: k * n + n] = eta
            post_exec[i + 2 * n, k * n: k * n + n] = eta

            pi_alloc[i + 2 * n, k * n: k * n + n] = (1 / eta)

            # Execution rates for transitions alloc lambda^alloc = eta * lambda^exec
            lambda_vector_alloc[k * n:k * n + n] = eta * eta  # The F will be controlled online

            # Execution rates for transitions exec for CPU_k lambda^exec = eta * F
            lambda_vector_exec[k * n:k * n + n] = eta  # The F will be controlled online

            # Initial condition
            mo[i + 2 * n, 0] = 1

        self.mo_proc = mo

        self.pre_alloc_proc: scipy.sparse.csr_matrix = pre_alloc.tocsr()
        self.post_alloc_proc: scipy.sparse.csr_matrix = post_alloc.tocsr()
        self.pi_alloc_proc: scipy.sparse.csr_matrix = pi_alloc.tocsr()
        self.lambda_vector_alloc_proc = lambda_vector_alloc

        self.pre_exec_proc: scipy.sparse.csr_matrix = pre_exec.tocsr()
        self.post_exec_proc: scipy.sparse.csr_matrix = post_exec.tocsr()
        self.pi_exec_proc: scipy.sparse.csr_matrix = pi_exec.tocsr()
        self.lambda_vector_exec_proc = lambda_vector_exec
