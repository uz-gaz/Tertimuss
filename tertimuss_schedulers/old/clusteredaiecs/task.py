# from dataclasses import dataclass


# @dataclass
class ImplicitDeadlineTask:
    def __init__(self, c: int, d: int):
        # Task worst case execution time in cycles
        self.c: int = c

        # Task deadline in cycles
        self.d: int = d
