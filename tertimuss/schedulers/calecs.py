from typing import Set, Dict, Optional, Tuple

from tertimuss.simulation_lib.schedulers_definition import CentralizedAbstractScheduler
from tertimuss.simulation_lib.system_definition import ProcessorDefinition, EnvironmentSpecification, TaskSet


class CALECSScheduler(CentralizedAbstractScheduler):
    def __init__(self):
        super().__init__(True)

    def check_schedulability(self, processor_definition: ProcessorDefinition,
                             environment_specification: EnvironmentSpecification, task_set: TaskSet) -> [bool,
                                                                                                         Optional[str]]:
        pass

    def offline_stage(self, processor_definition: ProcessorDefinition,
                      environment_specification: EnvironmentSpecification, task_set: TaskSet) -> int:
        pass

    def schedule_policy(self, global_time: float, active_jobs_id: Set[int], jobs_being_executed_id: Dict[int, int],
                        cores_frequency: int, cores_max_temperature: Optional[Dict[int, float]]) -> Tuple[
        Dict[int, int], Optional[int], Optional[int]]:
        pass
