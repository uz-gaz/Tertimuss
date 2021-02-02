from dataclasses import dataclass
from typing import List, Dict, Optional

from tertimuss.cubed_space_thermal_simulator import TemperatureLocatedCube


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
    time: float  # Time-stamp of the deadline miss
    jobs_and_cc: Dict[int, int]  # Jobs with remaining cc and the remaining cc


@dataclass
class RawSimulationResult:
    # Scheduler task set acceptance
    have_been_scheduled: bool  # This property is True if the scheduler agrees to schedule the task set in the provided
    # system
    scheduler_acceptance_error_message: Optional[str]  # This property only will take a value if have_been_scheduled is
    # False. It contains the scheduler's reason for not scheduling the task set in the provided system

    # Simulation results
    job_sections_execution: Dict[int, List[JobSectionExecution]]  # This property contains the list of jobs executed by
    # each core
    cpus_frequencies: Dict[int, List[CPUUsedFrequency]]  # This property contains the list of CPU frequencies used by
    # each core
    scheduling_points: List[float]  # This property contains the timestamps of the dynamic component of the scheduler
    # invocation
    temperature_measures: Dict[float, Dict[int, TemperatureLocatedCube]]  # This property contains a list with the
    # evolution of the processors' temperature
    hard_real_time_deadline_missed_stack_trace: Optional[SimulationStackTraceHardRTDeadlineMissed]  # This property only
    # takes value if the system misses a hard real-time deadline. It contains a snapshot of the system when the deadline
    # miss happens
    memory_usage_record: Optional[Dict[float, int]]  # This property has a record of the memory usage in bytes
