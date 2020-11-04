from dataclasses import dataclass
from typing import List, Tuple, Dict, Set, Optional, Union

from ._simulation_result import RawSimulationResult
from .._math_utils import list_lcm
from ..schedulers_definition import CentralizedAbstractScheduler
from ..system_definition import Job, TaskSet, HomogeneousCpuSpecification, EnvironmentSpecification


@dataclass
class SimulationOptionsSpecification:
    # True if is a debug simulation and debug messages should be showed
    id_debug: bool

    # True if want to simulate the thermal behaviour
    simulate_thermal_behaviour: bool


def _create_deadline_arrive_dict(lcm_frequency: int, jobs: List[Job]) -> Tuple[Dict[int, Set[int]],
                                                                               Dict[int, Set[int]]]:
    """
    Return a list ordered by arrive and by deadline of jobs containing the id of each job
    :param lcm_frequency:
    :param jobs:
    :return:
    """
    # Dict of activations
    activation_dict: Dict[int, Set[int]] = {}
    for i in jobs:
        normalized_activation = round(i.activation_time * lcm_frequency)
        if activation_dict.__contains__(normalized_activation):
            activation_dict[normalized_activation].add(i.identification)
        else:
            activation_dict[normalized_activation] = {i.identification}

    # Dict of deadlines
    deadlines_dict: Dict[int, Set[int]] = {}
    for i in jobs:
        normalized_absolute_deadline = round(i.absolute_deadline * lcm_frequency)
        if deadlines_dict.__contains__(normalized_absolute_deadline):
            deadlines_dict[normalized_absolute_deadline].add(i.identification)
        else:
            deadlines_dict[normalized_absolute_deadline] = {i.identification}

    return activation_dict, deadlines_dict


def execute_simulation(simulation_start_time: float,
                       simulation_end_time: float,
                       jobs: List[Job],
                       tasks: TaskSet,
                       cpu_specification: Union[HomogeneousCpuSpecification],
                       environment_specification: EnvironmentSpecification,
                       scheduler: CentralizedAbstractScheduler,
                       simulation_options: SimulationOptionsSpecification) -> Optional[RawSimulationResult]:
    # Check if scheduler is capable of execute task set
    can_schedule, error_message = scheduler.check_schedulability(cpu_specification, environment_specification, tasks)

    if not can_schedule:
        if error_message is not None:
            print("The scheduler can't schedule due to: ", error_message)
        else:
            print("The scheduler can't schedule")
        return None

    # Run scheduler offline phase
    cpu_frequency = scheduler.offline_stage(cpu_specification, environment_specification, tasks)

    # Create data structures for the simulation
    # Max frequency
    lcm_frequency = list_lcm(list(cpu_specification.cores_specification.available_frequencies))

    # Dict with activation and deadlines
    activation_dict, deadlines_dict = _create_deadline_arrive_dict(lcm_frequency, jobs)

    # Remaining jobs CC dict by id
    remaining_cc_dict: Dict[int, int] = {i.identification: i.execution_time for i in jobs}

    # Simulation step
    actual_lcm_cycle = simulation_start_time * lcm_frequency
    final_lcm_cycle = simulation_start_time * lcm_frequency

    # Main control loop
    while actual_lcm_cycle < final_lcm_cycle:
        pass
