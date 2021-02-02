import unittest

from tertimuss.analysis import obtain_deadline_misses_analysis, obtain_preemptions_migrations_analysis
from tertimuss.schedulers.g_edf import GEDFScheduler
from tertimuss.simulation_lib.simulator import execute_scheduler_simulation_simple, SimulationOptionsSpecification
from tertimuss.simulation_lib.system_definition import PeriodicTask, PreemptiveExecution, Criticality, AperiodicTask, \
    TaskSet, Job
from tertimuss.simulation_lib.system_definition.utils import generate_default_cpu, default_environment_specification
from tertimuss.visualization import generate_task_execution_plot, generate_job_execution_plot


class GettingStartedTest(unittest.TestCase):

    def test_getting_started(self):
        # Simulation configuration
        base_frequency = 1000
        available_frequencies = {base_frequency}
        number_of_cores = 2

        # Tasks definition
        periodic_tasks = [
            PeriodicTask(identification=1,
                         worst_case_execution_time=600,
                         relative_deadline=1,
                         best_case_execution_time=None,
                         execution_time_distribution=None,
                         memory_footprint=None,
                         priority=None,
                         preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                         deadline_criteria=Criticality.HARD,
                         energy_consumption=None,
                         phase=None,
                         period=1),
            PeriodicTask(identification=2,
                         worst_case_execution_time=1800,
                         relative_deadline=3,
                         best_case_execution_time=None,
                         execution_time_distribution=None,
                         memory_footprint=None,
                         priority=None,
                         preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                         deadline_criteria=Criticality.HARD,
                         energy_consumption=None,
                         phase=None,
                         period=3),
            PeriodicTask(identification=3,
                         worst_case_execution_time=600,
                         relative_deadline=3,
                         best_case_execution_time=None,
                         execution_time_distribution=None,
                         memory_footprint=None,
                         priority=None,
                         preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                         deadline_criteria=Criticality.HARD,
                         energy_consumption=None,
                         phase=None,
                         period=3)
        ]

        aperiodic_task = AperiodicTask(identification=0,
                                       worst_case_execution_time=600,
                                       relative_deadline=1,
                                       best_case_execution_time=None,
                                       execution_time_distribution=None,
                                       memory_footprint=None,
                                       priority=None,
                                       preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                                       deadline_criteria=Criticality.HARD,
                                       energy_consumption=None
                                       )

        aperiodic_tasks = [
            aperiodic_task
        ]

        # Jobs definition for aperiodic tasks
        aperiodic_jobs = [Job(0, aperiodic_task, 2)]

        # Task set definition
        task_set = TaskSet(
            periodic_tasks=periodic_tasks,
            aperiodic_tasks=aperiodic_tasks,
            sporadic_tasks=[]
        )

        # Execute simulation
        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=task_set,
            aperiodic_tasks_jobs=aperiodic_jobs,
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationOptionsSpecification(id_debug=True),
            scheduler=GEDFScheduler(activate_debug=True)
        )

        # Display tasks execution
        fig = generate_task_execution_plot(task_set=task_set, schedule_result=simulation_result,
                                           title="Task execution",
                                           outline_boxes=True)
        # fig.savefig("task_execution.svg")

        # Obtain tasks to jobs association
        periodic_tasks_jobs_association = [(i.task.identification, i.identification) for i in periodic_jobs]
        print(periodic_tasks_jobs_association)

        # Display jobs execution
        fig = generate_job_execution_plot(task_set=task_set, schedule_result=simulation_result,
                                          jobs=periodic_jobs + aperiodic_jobs,
                                          title="Task execution",
                                          outline_boxes=True)
        # fig.savefig("jobs_execution.svg")

        # Obtain migrations and preemption metrics
        migration_preemption_metrics = obtain_preemptions_migrations_analysis(task_set=task_set,
                                                                              schedule_result=simulation_result,
                                                                              jobs=periodic_jobs + aperiodic_jobs)

        print(migration_preemption_metrics.number_of_preemptions,
              migration_preemption_metrics.number_of_preemptions_by_job)

        # Obtain deadline misses analysis
        deadlines_misses_metrics = obtain_deadline_misses_analysis(task_set=task_set,
                                                                   schedule_result=simulation_result,
                                                                   jobs=periodic_jobs + aperiodic_jobs)
        print(deadlines_misses_metrics.number_of_missed_deadlines)
