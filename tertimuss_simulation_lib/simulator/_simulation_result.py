from dataclasses import dataclass
from typing import List, Dict, Optional

from cubed_space_thermal_simulator import TemperatureLocatedCube


@dataclass
class JobSectionExecution:
    job_id: int  # Job that have been executed
    task_id: int  # Task that have been executed
    execution_start_time: float  # When the job section start to execute in absolute seconds
    execution_end_time: float  # When the job section start to execute in absolute seconds
    number_of_executed_cycles: int  # Number of cycles executed in this interval


@dataclass
class CPUUsedFrequency:
    frequency_used: int  # Frequency used in Hz
    frequency_set_time: float  # When the frequency is set in absolute seconds
    frequency_unset_time: float  # When the frequency is unset in absolute seconds


@dataclass
class SimulationStackTraceHardRTDeadlineMissed:
    time: float

    # Jobs with remaining cc and the remaining cc
    jobs_and_cc: Dict[int, int]


@dataclass
class RawSimulationResult:
    # Scheduler task set acceptance
    have_been_scheduled: bool  # This will be true if the scheduler agree to schedule the task set
    scheduler_acceptance_error_message: Optional[str]  # Only will take value if have_been_scheduled is False. This will
    # contain the scheduler reason

    # Simulation results
    job_sections_execution: Dict[int, List[JobSectionExecution]]  # List of jobs executed by each core
    cpus_frequencies: Dict[int, List[CPUUsedFrequency]]  # List of CPU frequencies used by each core
    scheduling_points: List[float]  # Points where the scheduler have made an scheduling
    temperature_measures: Dict[float, List[TemperatureLocatedCube]]  # Measures of temperature
    hard_real_time_deadline_missed_stack_trace: Optional[SimulationStackTraceHardRTDeadlineMissed]  # Only will take
    # value if a hard real time is missed
