class BaseSchedulerTask(object):
    def __init__(self, d: float, a: float, c: int, task_id: int):
        """
        This class represent a job, where next_deadline is the deadline of the job and next_arrival the arrival of the
         job
        :param d: deadline
        :param a: arrival
        :param c: execution time in cycles
        :param task_id: id
        """
        self.next_deadline = d  # next task deadline in absolute seconds (since simulation start)
        self.next_arrival = a  # next task arrival in absolute seconds (since simulation start)
        self.pending_c = c  # pending execution in cycles
        self.id = task_id  # task id (always natural integer)
