from dataclasses import dataclass
from typing import List, Dict

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
class RawSimulationResult:
    job_sections_execution: Dict[int, List[JobSectionExecution]]  # List of jobs executed by each core
    cpus_frequencies: Dict[int, List[CPUUsedFrequency]]  # List of CPU frequencies used by each core
    scheduling_points: List[float]  # Points where the scheduler have made an scheduling
    temperature_measures: Dict[float, List[TemperatureLocatedCube]]  # Measures of temperature
