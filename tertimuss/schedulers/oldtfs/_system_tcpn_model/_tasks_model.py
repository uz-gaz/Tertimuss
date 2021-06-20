import numpy
import scipy.sparse

from tertimuss.simulation_lib.system_definition import TaskSet, Processor


class TasksModel(object):
    """
    Create the TCPN that represents the task model
    """

    def __init__(self, cpu_specification: Processor,
                 task_set: TaskSet,
                 simulation_precision):
        n_periodic = len(task_set.periodic_tasks)
        n_aperiodic = len(task_set.aperiodic_tasks)
        m = len(cpu_specification.cores_definition)
        common_core_specification = cpu_specification.cores_definition[0].core_type

        base_frequency = max(common_core_specification.available_frequencies)
        # total of places of the TCPN ((p^w_i,p^cc_i) for each task)
        p = 2 * n_periodic + n_aperiodic

        # Total of transitions ((t^w_i and ti,jAlloc for each processor) for each task)
        t_w = n_periodic

        # n transitions of tasks period and n * m transitions alloc ((ti,jAlloc for each processor) for each task)
        t_alloc = (n_periodic + n_aperiodic) * m

        # Task model definition
        pre = scipy.sparse.lil_matrix((p, t_w), dtype=simulation_precision)
        post = scipy.sparse.lil_matrix((p, t_w), dtype=simulation_precision)
        pi = scipy.sparse.lil_matrix((p, t_w), dtype=simulation_precision)
        lambda_vector = numpy.zeros(t_w, dtype=simulation_precision)
        mo = numpy.zeros((p, 1), dtype=simulation_precision)

        # Construction of Pre an Post matrix for places(p^w_i,p^cc_i) and transition(t^w_i)
        pre[:n_periodic, :] = scipy.sparse.identity(n_periodic, dtype=simulation_precision,
                                                    format="lil")  # Transition from p^w_i to t^w_i
        post[:n_periodic, :] = scipy.sparse.identity(n_periodic, dtype=simulation_precision,
                                                     format="lil")  # Transition from t^w_i to p^w_i
        post[n_periodic: 2 * n_periodic, :] = scipy.sparse.identity(n_periodic,
                                                                    dtype=simulation_precision,
                                                                    format="lil")  # Transition from t^w_i to p^cc_i
        lambda_vector[:] = numpy.asarray([task.period for task in task_set.periodic_tasks],
                                         dtype=simulation_precision)
        pi[:n_periodic, :] = scipy.sparse.identity(n_periodic, dtype=simulation_precision,
                                                   format="lil")  # Transition from p^w_i to t^w_i
        mo[: n_periodic, 0] = 1  # Marking in p^w_i
        mo[n_periodic: 2 * n_periodic, 0] = numpy.asarray(
            [task.worst_case_execution_time / base_frequency for task in task_set.periodic_tasks],
            dtype=simulation_precision)  # Marking in p^cc_i periodic
        mo[2 * n_periodic: 2 * n_periodic + n_aperiodic, 0] = numpy.asarray(
            [task.worst_case_execution_time / base_frequency for task in task_set.aperiodic_tasks],
            dtype=simulation_precision)  # Marking in p^cc_i aperiodic

        # Task model union with processor model definition
        pre_alloc = scipy.sparse.lil_matrix((p, t_alloc), dtype=simulation_precision)
        post_alloc = scipy.sparse.lil_matrix((p, t_alloc), dtype=simulation_precision)
        pi_alloc = scipy.sparse.lil_matrix((p, t_alloc), dtype=simulation_precision)
        # Lambda vector alloc will be defined in processor model

        # Construction of Pre an Post matrix for Transitions alloc
        pre_alloc[n_periodic:, :] = scipy.sparse.hstack([scipy.sparse.identity(n_periodic + n_aperiodic,
                                                                               dtype=simulation_precision,
                                                                               format="lil") for _ in range(m)])

        # pi_alloc = pre_alloc.copy()

        # Definition of task model
        self.pre_tau: scipy.sparse.csr_matrix = pre.tocsr()
        self.post_tau: scipy.sparse.csr_matrix = post.tocsr()
        self.pi_tau: scipy.sparse.csr_matrix = pi.tocsr()
        self.lambda_vector_tau = lambda_vector
        self.mo_tau = mo

        # Definition of the union between the task model and the processor model
        self.pre_alloc_tau: scipy.sparse.csr_matrix = pre_alloc.tocsr()
        self.post_alloc_tau: scipy.sparse.csr_matrix = post_alloc.tocsr()
        self.pi_alloc_tau: scipy.sparse.csr_matrix = pi_alloc.tocsr()
