from typing import Optional


class Task(object):
    """
    Task specification
    """

    def __init__(self, c: int, e: Optional[float]):
        """
        :param c: Task worst case execution time in cycles
        :param e: Energy consumption
        """
        self.c: int = c
        self.e: Optional[float] = e
