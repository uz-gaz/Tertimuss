import scipy

from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class TasksModel(object):
    """
        Represents the Task arrival and CPU'S Module in the paper
    """

    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification):

        n = len(tasks_specification.tasks)
        m = cpu_specification.number_of_cores

        # total of places of the TCPN ((p^w_i,p^cc_i) for each task)
        p = 2 * n

        # Total of transitions ((t^w_i and ti,jAlloc for each processor) for each task)
        t = n

        # n transitions of tasks period and n * m transitions alloc ((ti,jAlloc for each processor) for each task)
        t_alloc = n * m

        # Task model definition
        pre = scipy.zeros((p, t))
        post = scipy.zeros((p, t))
        pi = scipy.zeros((p, t))
        lambda_vector = scipy.zeros(t)
        mo = scipy.zeros((p, 1))

        # Construction of Pre an Post matrix for places(p^w_i,p^cc_i) and transition(t^w_i)
        for k in range(n):
            i = 2 * k
            pre[i, k] = 1  # Transition from p^w_i to t^w_i
            post[i:i + 2, k] = [1,
                                tasks_specification.tasks[k].c]  # Transition from t^w_i to p^w_i, from t^w_i to p^cc_i
            lambda_vector[k] = 1 / tasks_specification.tasks[k].t
            pi[i, k] = 1
            mo[i: i + 2, 0] = [1, tasks_specification.tasks[k].c]

        # Task model union with processor model definition
        pre_alloc = scipy.zeros((p, t_alloc))
        post_alloc = scipy.zeros((p, t_alloc))
        pi_alloc = scipy.zeros((p, t_alloc))
        # Lambda vector alloc will be defined in processor model

        # Construction of Pre an Post matrix for Transitions alloc
        for k in range(n):
            i = 2 * k
            for r in range(m):
                j = r * n + k
                pre_alloc[i + 1, j] = 1
                pi_alloc[i + 1, j] = 1

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
