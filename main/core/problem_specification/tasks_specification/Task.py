from typing import Optional


class Task(object):

    def __init__(self, c: int, e: Optional[float]):
        """
        Task specification

        :param c: Task worst case execution time in cycles
        :param e: Energy consumption
        """
        self.c: int = c
        self.e: Optional[float] = e
