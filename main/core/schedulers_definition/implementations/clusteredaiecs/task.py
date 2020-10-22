
from dataclasses import dataclass


@dataclass
class ImplicitDeadlineTask:
    # Task worst case execution time in cycles
    c: int

    # Task deadline in cycles
    d: int
