import unittest
from tertimuss.schedulers.alecs import ALECSScheduler
from tertimuss.simulation_lib.simulator import execute_scheduler_simulation_simple, SimulationOptionsSpecification
from tertimuss.simulation_lib.system_definition import TaskSet, PeriodicTask, PreemptiveExecution, Criticality
from tertimuss.simulation_lib.system_definition.utils import generate_default_cpu, default_environment_specification
from tertimuss.tasks_generator.deadline_generator import UniformIntegerDeadlineGenerator
from tertimuss.tasks_generator.periodic_tasks.implicit_deadlines import UUniFastDiscard
from tertimuss.visualization_generator import generate_task_execution_plot


class ReadmeExampleTest(unittest.TestCase):

    def test_readme_example(self):
        # Simulation configuration
        base_frequency = 1000
        available_frequencies = {base_frequency}
        number_of_cores = 4
        number_of_tasks = 9

        # Task generation
        tasks_deadlines = UniformIntegerDeadlineGenerator.generate(number_of_tasks=number_of_tasks,
                                                                   min_deadline=2,
                                                                   max_deadline=12,
                                                                   major_cycle=24)
        x = UUniFastDiscard.generate(utilization=number_of_cores,
                                     tasks_deadlines=tasks_deadlines,
                                     processor_frequency=base_frequency)

        # Definition of the task set
        task_set = TaskSet(
            periodic_tasks=[
                PeriodicTask(identification=i,
                             worst_case_execution_time=j.worst_case_execution_time,
                             relative_deadline=j.deadline,
                             best_case_execution_time=None,
                             execution_time_distribution=None,
                             memory_footprint=None,
                             priority=None,
                             preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                             deadline_criteria=Criticality.HARD,
                             energy_consumption=None,
                             phase=None,
                             period=j.deadline) for i, j in enumerate(x)],
            aperiodic_tasks=[],
            sporadic_tasks=[]
        )

        # Execute simulation
        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=task_set,
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationOptionsSpecification(id_debug=True),
            scheduler=ALECSScheduler(activate_debug=True)
        )

        # Display execution
        fig = generate_task_execution_plot(task_set=task_set, schedule_result=simulation_result,
                                           title="Task execution",
                                           outline_boxes=True)
        # fig.show()
