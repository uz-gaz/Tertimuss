from typing import Optional


class Task(object):
    """
    Task specification
    """

    def __init__(self, c: float, e: Optional[float]):
        """
        :param c: Task worst case execution time in seconds at base frequency
        :param e: Energy consumption
        """
        self.c: float = c
        self.e: Optional[float] = e