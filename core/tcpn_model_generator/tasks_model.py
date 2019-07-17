import scipy

from core.problem_specification.CpuSpecification import CpuSpecification
from core.problem_specification.TasksSpecification import TasksSpecification


class TasksModel(object):
    """
        Represents the Task arrival and CPU'S Module in the paper
    """

    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification):
        n_periodic = len(tasks_specification.periodic_tasks)
        n_aperiodic = len(tasks_specification.aperiodic_tasks)
        m = cpu_specification.number_of_cores

        # total of places of the TCPN ((p^w_i,p^cc_i) for each task)
        p = 2 * n_periodic + n_aperiodic

        # Total of transitions ((t^w_i and ti,jAlloc for each processor) for each task)
        t_w = n_periodic

        # n transitions of tasks period and n * m transitions alloc ((ti,jAlloc for each processor) for each task)
        t_alloc = (n_periodic + n_aperiodic) * m

        # Task model definition
        pre = scipy.zeros((p, t_w))
        post = scipy.zeros((p, t_w))
        pi = scipy.zeros((p, t_w))
        lambda_vector = scipy.zeros(t_w)
        mo = scipy.zeros((p, 1))

        # Construction of Pre an Post matrix for places(p^w_i,p^cc_i) and transition(t^w_i)
        pre[:n_periodic, :] = scipy.identity(n_periodic)  # Transition from p^w_i to t^w_i
        post[:n_periodic, :] = scipy.identity(n_periodic)  # Transition from t^w_i to p^w_i
        post[n_periodic: 2 * n_periodic, :] = scipy.identity(n_periodic)  # Transition from t^w_i to p^cc_i
        lambda_vector[:] = 1 / scipy.asarray([task.t for task in tasks_specification.periodic_tasks])
        pi[:n_periodic, :] = scipy.identity(n_periodic)  # Transition from p^w_i to t^w_i
        mo[: n_periodic, 0] = scipy.ones(n_periodic)  # Marking in p^w_i
        mo[n_periodic: 2 * n_periodic, 0] = scipy.asarray(
            [task.c for task in tasks_specification.periodic_tasks])  # Marking in p^cc_i periodic
        mo[2 * n_periodic: 2 * n_periodic + n_aperiodic, 0] = scipy.asarray(
            [task.c for task in tasks_specification.aperiodic_tasks])  # Marking in p^cc_i aperiodic

        # Task model union with processor model definition
        pre_alloc = scipy.zeros((p, t_alloc))
        post_alloc = scipy.zeros((p, t_alloc))
        pi_alloc = scipy.zeros((p, t_alloc))
        # Lambda vector alloc will be defined in processor model

        # Construction of Pre an Post matrix for Transitions alloc
        pre_alloc[n_periodic:, :] = scipy.concatenate(m * [scipy.identity(n_periodic + n_aperiodic)], axis=1)

        # Definition of task model
        self.pre_tau = pre
        self.post_tau = post
        self.pi_tau = pi
        self.lambda_vector_tau = lambda_vector
        self.mo_tau = mo

        # Definition of the union between the task model and the processor model
        self.pre_alloc_tau = pre_alloc
        self.post_alloc_tau = post_alloc
        self.pi_alloc_tau = pi_alloc
