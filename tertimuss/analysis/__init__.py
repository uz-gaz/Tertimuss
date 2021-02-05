"""
==============
Analysis tools
==============

Set of tools to analyze the result of the simulations done with tertimuss.

This module provides the following functions:
- :function:`.obtain_deadline_misses_analysis`
- :function:`.obtain_non_preemptive_tasks_retries_analysis`
- :function:`.obtain_preemptions_migrations_analysis`

It also exposes the following classes related with the previous functions:
- :class:`DeadlineMissedAnalysis`
- :class:`NonPreemptiveTasksRetryAnalysis`
- :class:`PreemptionsMigrationsAnalysis`
"""

from ._deadline_missed_analysis import DeadlineMissedAnalysis, obtain_deadline_misses_analysis
from ._non_preemptive_tasks_retry_analysis import NonPreemptiveTasksRetryAnalysis, \
    obtain_non_preemptive_tasks_retries_analysis
from ._preemptions_migrations_analysis import PreemptionsMigrationsAnalysis, obtain_preemptions_migrations_analysis
