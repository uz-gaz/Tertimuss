import unittest

from typing import Optional

from matplotlib import pyplot

from tertimuss_plot_generator._task_assignation_plot import generate_task_assignation_plot
from tertimuss_simulation_lib.simulator import RawSimulationResult, JobSectionExecution, CPUUsedFrequency
from tertimuss_simulation_lib.system_definition import PeriodicTask, PreemptiveExecution, Criticality, TaskSet


class TaskAssignationPlotTest(unittest.TestCase):
    @staticmethod
    def __create_implicit_deadline_periodic_task_h_rt(task_id: int, worst_case_execution_time: int,
                                                      period: float, priority: Optional[int]) -> PeriodicTask:
        # Create implicit deadline task with priority equal to identification id
        return PeriodicTask(identification=task_id,
                            worst_case_execution_time=worst_case_execution_time,
                            relative_deadline=period,
                            best_case_execution_time=None,
                            execution_time_distribution=None,
                            memory_footprint=None,
                            priority=priority,
                            preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                            deadline_criteria=Criticality.HARD,
                            energy_consumption=None,
                            phase=None,
                            period=period)

    def test_tasks_assignation_plot(self):
        periodic_tasks = [
            self.__create_implicit_deadline_periodic_task_h_rt(3, 3000, 7.0, 3),
            self.__create_implicit_deadline_periodic_task_h_rt(2, 4000, 7.0, 2),
            self.__create_implicit_deadline_periodic_task_h_rt(1, 4000, 14.0, 1),
            self.__create_implicit_deadline_periodic_task_h_rt(0, 3000, 14.0, 0)
        ]

        tasks = TaskSet(
            periodic_tasks=periodic_tasks,
            aperiodic_tasks=[],
            sporadic_tasks=[]
        )

        simulation_result = RawSimulationResult(have_been_scheduled=True, scheduler_acceptance_error_message=None,
                                                job_sections_execution={0: [
                                                    JobSectionExecution(job_id=0, task_id=3, execution_start_time=0.0,
                                                                        execution_end_time=3.0,
                                                                        number_of_executed_cycles=3000),
                                                    JobSectionExecution(job_id=2, task_id=2, execution_start_time=3.0,
                                                                        execution_end_time=4.0,
                                                                        number_of_executed_cycles=1000),
                                                    JobSectionExecution(job_id=4, task_id=1, execution_start_time=4.0,
                                                                        execution_end_time=7.0,
                                                                        number_of_executed_cycles=3000),
                                                    JobSectionExecution(job_id=1, task_id=3, execution_start_time=7.0,
                                                                        execution_end_time=10.0,
                                                                        number_of_executed_cycles=3000),
                                                    JobSectionExecution(job_id=3, task_id=2, execution_start_time=10.0,
                                                                        execution_end_time=11.0,
                                                                        number_of_executed_cycles=1000)], 1: [
                                                    JobSectionExecution(job_id=2, task_id=2, execution_start_time=0.0,
                                                                        execution_end_time=3.0,
                                                                        number_of_executed_cycles=3000),
                                                    JobSectionExecution(job_id=4, task_id=1, execution_start_time=3.0,
                                                                        execution_end_time=4.0,
                                                                        number_of_executed_cycles=1000),
                                                    JobSectionExecution(job_id=5, task_id=0, execution_start_time=4.0,
                                                                        execution_end_time=7.0,
                                                                        number_of_executed_cycles=3000),
                                                    JobSectionExecution(job_id=3, task_id=2, execution_start_time=7.0,
                                                                        execution_end_time=10.0,
                                                                        number_of_executed_cycles=3000)]},
                                                cpus_frequencies={0: [
                                                    CPUUsedFrequency(frequency_used=1000, frequency_set_time=0.0,
                                                                     frequency_unset_time=14.0)], 1: [
                                                    CPUUsedFrequency(frequency_used=1000, frequency_set_time=0.0,
                                                                     frequency_unset_time=14.0)]},
                                                scheduling_points=[0.0, 3.0, 4.0, 7.0, 10.0], temperature_measures={},
                                                hard_real_time_deadline_missed_stack_trace=None)

        fig = generate_task_assignation_plot(task_set=tasks, schedule_result=simulation_result,
                                             title="Task assignation")
        fig.show()
