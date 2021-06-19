import unittest
from typing import Dict

from matplotlib import pyplot as plt

from tertimuss.schedulers._oldtfs import SOLDTFS
from tertimuss.simulation_lib.simulator import execute_scheduler_simulation_simple, SimulationConfiguration
from tertimuss.simulation_lib.system_definition import TaskSet, PeriodicTask, PreemptiveExecution, Criticality
from tertimuss.simulation_lib.system_definition.utils import generate_default_cpu, default_environment_specification


class OLDTFSTest(unittest.TestCase):
    @staticmethod
    def create_implicit_deadline_periodic_task_s_rt(task_id: int, worst_case_execution_time: int,
                                                    period: float) -> PeriodicTask:
        # Create implicit deadline task with priority equal to identification id
        return PeriodicTask(identifier=task_id,
                            worst_case_execution_time=worst_case_execution_time,
                            relative_deadline=period,
                            best_case_execution_time=None,
                            execution_time_distribution=None,
                            memory_footprint=None,
                            priority=None,
                            preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                            deadline_criteria=Criticality.SOFT,
                            energy_consumption=None,
                            phase=None,
                            period=period)

    def test_simple_simulation_periodic_task_set(self):
        periodic_tasks = [
            self.create_implicit_deadline_periodic_task_s_rt(0, 1000, 20.0),
            self.create_implicit_deadline_periodic_task_s_rt(1, 500, 10.0),
            self.create_implicit_deadline_periodic_task_s_rt(2, 700, 10.0),
            self.create_implicit_deadline_periodic_task_s_rt(3, 700, 10.0),
            self.create_implicit_deadline_periodic_task_s_rt(4, 700, 10.0),
            self.create_implicit_deadline_periodic_task_s_rt(5, 1400, 20.0)
        ]

        task_set = TaskSet(
            periodic_tasks=periodic_tasks,
            aperiodic_tasks=[],
            sporadic_tasks=[]
        )

        number_of_cores = 5
        available_frequencies = {100}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=task_set,
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies, 0),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True),
            scheduler=SOLDTFS(240, simulate_thermal=False)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled

        # Check the percentage of execution accomplished (by implementation the OLDTFS control won't
        # accomplish full execution of the tasks)
        cycles_per_task_in_major_cycle: Dict[int, int] = {
            i.identifier: i.worst_case_execution_time * round(20 / i.relative_deadline)
            for i in periodic_tasks}
        executed_cycles_by_task: Dict[int, int] = {i: 0 for i in cycles_per_task_in_major_cycle.keys()}
        for i in simulation_result.job_sections_execution.values():
            for j in i:
                executed_cycles_by_task[j.task_id] = executed_cycles_by_task[j.task_id] + j.number_of_executed_cycles

        # In this task set it only accomplish a 70% of execution in all tasks (It should be reviewed)
        all((executed_cycles_by_task[i] / cycles_per_task_in_major_cycle[i]) > 0.7 for i in
            cycles_per_task_in_major_cycle.keys())
