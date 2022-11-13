import unittest
from tertimuss.schedulers.dce import SDeutschbeinCE
from tertimuss.simulation_lib.simulator import execute_scheduler_simulation_simple, SimulationConfiguration
from tertimuss.simulation_lib.system_definition import TaskSet
from tertimuss.simulation_lib.system_definition.utils import generate_default_cpu, default_environment_specification
from tests.schedulers._common_scheduler_tests_utils import create_implicit_deadline_periodic_task_h_rt, \
    periodic_implicit_deadline_tasks


class DeutschbeinCETest(unittest.TestCase):
    '''
    Testing class for the Deutschbein Cyclic Executive's Scheduler
    '''

    # --------------------------------------------------------------------------
    # Paper's task set tests

    def test_nonpreemptive_paper_task_set(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |                            job 6                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it uses the paper's task set
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 12.0)
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_nonpreemptive_mcnaughton_paper_task_set(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |                            job 6                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it uses the paper's task set
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 12.0)
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_preemptive_paper_task_set(self):
        '''
        - Preemption model:
            preemptive
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |                            job 6                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it uses the paper's task set
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 12.0),
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # --------------------------------------------------------------------------
    # Paper's task set on a single core platform

    def test_nonpreemptive_paper_task_set_one_core(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            1
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |                            job 6                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it uses the paper's task set on a single core platform
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 12.0)
        ]

        number_of_cores = 1
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_nonpreemptive_mcnaughton_paper_task_set_one_core(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            1
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |                            job 6                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it uses the paper's task set on a single core platform
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 12.0)
        ]

        number_of_cores = 1
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_preemptive_paper_task_set_one_core(self):
        '''
        - Preemption model:
            preemptive
        - Number of cores:
            1
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |                            job 6                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it uses the paper's task set on a single core platform
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 12.0),
        ]

        number_of_cores = 1
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # --------------------------------------------------------------------------
    # Repeated tasks tests

    def test_nonpreemptive_paper_task_set_repeated_tasks(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |            job 6            |            job 7            |
                    |---------|---------|---------|---------|---------|---------|
            Task 4  |                            job 8                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it's the paper's task set, but it introduces new tasks to schedule with the same features than the existing ones,
            so that the system's workload is increased keeping an analysis which is similar to the paper's example
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(4, 80, 12.0),
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_nonpreemptive_mcnaughton_paper_task_set_repeated_tasks(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |            job 6            |            job 7            |
                    |---------|---------|---------|---------|---------|---------|
            Task 4  |                            job 8                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it's the paper's task set, but it introduces new tasks to schedule with the same features than the existing ones,
            so that the system's workload is increased keeping an analysis which is similar to the paper's example
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(4, 80, 12.0),
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_preemptive_paper_task_set_repeated_tasks(self):
        '''
        - Preemption model:
            preemptive
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |            job 6            |            job 7            |
                    |---------|---------|---------|---------|---------|---------|
            Task 4  |                            job 8                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it's the paper's task set, but it introduces new tasks to schedule with the same features than the existing ones,
            so that the system's workload is increased keeping an analysis which is similar to the paper's example
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(4, 80, 12.0),
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # --------------------------------------------------------------------------
    # Repeated tasks test, but giving the minimal frequency as available

    def test_nonpreemptive_paper_task_set_repeated_tasks_minimal_frequency(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30, 40, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |            job 6            |            job 7            |
                    |---------|---------|---------|---------|---------|---------|
            Task 4  |                            job 8                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it's the paper's task set, but it introduces new tasks to schedule with the same features than the existing ones,
            so that the system's workload is increased keeping an analysis which is similar to the paper's example. Moreover,
            now the minimal frequency required is given as available, so that it will be chosen by the scheduler and the tasks'
            execution will exactly fit the minor cycle

            NOTE: the frequencies must be integer numbers, and that's why this example is taken, because the minimal frequency
            for the schedule fits that requirement
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(4, 80, 12.0),
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30, 40, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_nonpreemptive_mcnaughton_paper_task_set_repeated_tasks_minimal_frequency(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30, 40, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |            job 6            |            job 7            |
                    |---------|---------|---------|---------|---------|---------|
            Task 4  |                            job 8                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it's the paper's task set, but it introduces new tasks to schedule with the same features than the existing ones,
            so that the system's workload is increased keeping an analysis which is similar to the paper's example. Moreover,
            now the minimal frequency required is given as available, so that it will be chosen by the scheduler and the tasks'
            execution will exactly fit the minor cycle

            NOTE: the frequencies must be integer numbers, and that's why this example is taken, because the minimal frequency
            for the schedule fits that requirement
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(4, 80, 12.0),
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30, 40, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_preemptive_paper_task_set_repeated_tasks_minimal_frequency(self):
        '''
        - Preemption model:
            preemptive
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 13, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |            job 6            |            job 7            |
                    |---------|---------|---------|---------|---------|---------|
            Task 4  |                            job 8                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it's the paper's task set, but it introduces new tasks to schedule with the same features than the existing ones,
            so that the system's workload is increased keeping an analysis which is similar to the paper's example. Moreover,
            now the minimal frequency required is given as available, so that it will be chosen by the scheduler and the tasks'
            execution will exactly fit the minor cycle

            NOTE: the frequencies must be integer numbers, and that's why this example is taken, because the minimal frequency
            for the schedule fits that requirement
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(4, 80, 12.0),
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 13, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # --------------------------------------------------------------------------
    # More cores with the repeated tasks set

    def test_nonpreemptive_paper_task_set_repeated_tasks_three_cores(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            3
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |            job 6            |            job 7            |
                    |---------|---------|---------|---------|---------|---------|
            Task 4  |                            job 8                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it's the paper's task set, but it introduces new tasks to schedule with the same features than the existing ones,
            so that the system's workload is increased keeping an analysis which is similar to the paper's example. Moreover,
            now the number of cores has been increased to three, so it might fit better the workload requested
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(4, 80, 12.0),
        ]

        number_of_cores = 3
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_nonpreemptive_mcnaughton_paper_task_set_repeated_tasks_three_cores(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            3
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |            job 6            |            job 7            |
                    |---------|---------|---------|---------|---------|---------|
            Task 4  |                            job 8                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it's the paper's task set, but it introduces new tasks to schedule with the same features than the existing ones,
            so that the system's workload is increased keeping an analysis which is similar to the paper's example. Moreover,
            now the number of cores has been increased to three, so it might fit better the workload requested
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(4, 80, 12.0),
        ]

        number_of_cores = 3
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_preemptive_paper_task_set_repeated_tasks_three_cores(self):
        '''
        - Preemption model:
            preemptive
        - Number of cores:
            3
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |            job 6            |            job 7            |
                    |---------|---------|---------|---------|---------|---------|
            Task 4  |                            job 8                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it's the paper's task set, but it introduces new tasks to schedule with the same features than the existing ones,
            so that the system's workload is increased keeping an analysis which is similar to the paper's example. Moreover,
            now the number of cores has been increased to three, so it might fit better the workload requested
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(4, 80, 12.0),
        ]

        number_of_cores = 3
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # --------------------------------------------------------------------------
    # Increasing the number of cores to four

    def test_nonpreemptive_four_cores(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            4
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4
                    |---------|---------|---------|---------|
            Task 1  |  job 1  |  job 2  |  job 3  |  job 4  |
                    |---------|---------|---------|---------|
            Task 2  |        job 5      |        job 6      |
                    |---------|---------|---------|---------|
            Task 3  |                  job 7                |
                    |---------|---------|---------|---------|
                    0         3         6         9         12
        - Commentaries for this test:
            New task set in which all the periods (and both the minor and the major cyle) are multiples of three. A 4-core
            platform is used for the simulation
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 30, 3.0),
            create_implicit_deadline_periodic_task_h_rt(2, 50, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 100, 12.0),
        ]

        number_of_cores = 4
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_nonpreemptive_mcnaughton_four_cores(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            4
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4
                    |---------|---------|---------|---------|
            Task 1  |  job 1  |  job 2  |  job 3  |  job 4  |
                    |---------|---------|---------|---------|
            Task 2  |        job 5      |        job 6      |
                    |---------|---------|---------|---------|
            Task 3  |                  job 7                |
                    |---------|---------|---------|---------|
                    0         3         6         9         12
        - Commentaries for this test:
            New task set in which all the periods (and both the minor and the major cyle) are multiples of three. A 4-core
            platform is used for the simulation
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 30, 3.0),
            create_implicit_deadline_periodic_task_h_rt(2, 50, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 100, 12.0),
        ]

        number_of_cores = 4
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_preemptive_four_cores(self):
        '''
        - Preemption model:
            preemptive
        - Number of cores:
            4
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4
                    |---------|---------|---------|---------|
            Task 1  |  job 1  |  job 2  |  job 3  |  job 4  |
                    |---------|---------|---------|---------|
            Task 2  |        job 5      |        job 6      |
                    |---------|---------|---------|---------|
            Task 3  |                  job 7                |
                    |---------|---------|---------|---------|
                    0         3         6         9         12
        - Commentaries for this test:
            New task set in which all the periods (and both the minor and the major cyle) are multiples of three. A 4-core
            platform is used for the simulation
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 30, 3.0),
            create_implicit_deadline_periodic_task_h_rt(2, 50, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 100, 12.0),
        ]

        number_of_cores = 4
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # --------------------------------------------------------------------------
    # Increasing the number of cores to five

    def test_nonpreemptive_five_cores(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            5
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6 | frame 7 | frame 8 | frame 9 | frame 10| frame 11| frame 12
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 1  |  job 1  |  job 2  |  job 3  |  job 4  |  job 5  |  job 6  |  job 7  |  job 8  |  job 9  | job 10  | job 11  | job 12  |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 2  |       job 13      |       job 14      |       job 15      |       job 16      |       job 17      |       job 18      |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 3  |           job 19            |           job 20            |           job 21            |           job 22            |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 4  |                 job 23                |                 job 24                |                 job 25                |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 5  |                            job 26                         |                            job 27                         |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 6  |                                                          job 28                                                       |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
                    0         7         14        21        28        35        42        49        56        63        70        77        84
        - Commentaries for this test:
            New task set in which all the periods (and both the minor and the major cyle) are multiples of seven. A 5-core
            platform is used for the simulation
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 30, 7.0),
            create_implicit_deadline_periodic_task_h_rt(2, 50, 14.0),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 21.0),
            create_implicit_deadline_periodic_task_h_rt(4, 100, 28.0),
            create_implicit_deadline_periodic_task_h_rt(5, 128, 42.0),
            create_implicit_deadline_periodic_task_h_rt(6, 256, 84.0),
        ]

        number_of_cores = 5
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_nonpreemptive_mcnaughton_five_cores(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            5
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6 | frame 7 | frame 8 | frame 9 | frame 10| frame 11| frame 12
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 1  |  job 1  |  job 2  |  job 3  |  job 4  |  job 5  |  job 6  |  job 7  |  job 8  |  job 9  | job 10  | job 11  | job 12  |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 2  |       job 13      |       job 14      |       job 15      |       job 16      |       job 17      |       job 18      |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 3  |           job 19            |           job 20            |           job 21            |           job 22            |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 4  |                 job 23                |                 job 24                |                 job 25                |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 5  |                            job 26                         |                            job 27                         |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 6  |                                                          job 28                                                       |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
                    0         7         14        21        28        35        42        49        56        63        70        77        84
        - Commentaries for this test:
            New task set in which all the periods (and both the minor and the major cyle) are multiples of seven. A 5-core
            platform is used for the simulation
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 30, 7.0),
            create_implicit_deadline_periodic_task_h_rt(2, 50, 14.0),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 21.0),
            create_implicit_deadline_periodic_task_h_rt(4, 100, 28.0),
            create_implicit_deadline_periodic_task_h_rt(5, 128, 42.0),
            create_implicit_deadline_periodic_task_h_rt(6, 256, 84.0),
        ]

        number_of_cores = 5
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_preemptive_five_cores(self):
        '''
        - Preemption model:
            preemptive
        - Number of cores:
            5
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6 | frame 7 | frame 8 | frame 9 | frame 10| frame 11| frame 12
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 1  |  job 1  |  job 2  |  job 3  |  job 4  |  job 5  |  job 6  |  job 7  |  job 8  |  job 9  | job 10  | job 11  | job 12  |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 2  |       job 13      |       job 14      |       job 15      |       job 16      |       job 17      |       job 18      |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 3  |           job 19            |           job 20            |           job 21            |           job 22            |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 4  |                 job 23                |                 job 24                |                 job 25                |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 5  |                            job 26                         |                            job 27                         |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
            Task 6  |                                                          job 28                                                       |
                    |---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
                    0         7         14        21        28        35        42        49        56        63        70        77        84
        - Commentaries for this test:
            New task set in which all the periods (and both the minor and the major cyle) are multiples of seven. A 5-core
            platform is used for the simulation
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 30, 7.0),
            create_implicit_deadline_periodic_task_h_rt(2, 50, 14.0),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 21.0),
            create_implicit_deadline_periodic_task_h_rt(4, 100, 28.0),
            create_implicit_deadline_periodic_task_h_rt(5, 128, 42.0),
            create_implicit_deadline_periodic_task_h_rt(6, 256, 84.0),
        ]

        number_of_cores = 5
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # --------------------------------------------------------------------------
    # Using the ALECS test's task set and platform

    def test_simple_simulation_periodic_task_set_nonpreemptive(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            5
        - Available frequencies (Hz):
            1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4
                    |---------|---------|---------|---------|
            Task 0  |                  job 1                |
                    |---------|---------|---------|---------|
            Task 1  |        job 2      |        job 3      |
                    |---------|---------|---------|---------|
            Task 2  |        job 4      |        job 5      |
                    |---------|---------|---------|---------|
            Task 3  |        job 6      |        job 7      |
                    |---------|---------|---------|---------|
            Task 4  |        job 8      |        job 9      |
                    |---------|---------|---------|---------|
            Task 5  |                 job 10                |
                    |---------|---------|---------|---------|
            Task 6  | job 11  | job 12  | job 13  | job 14  |
                    |---------|---------|---------|---------|
                    0         5         10        15        20
        - Commentaries for this test:
            This test is a copy of the ALECS test, using the Deutschbein CE scheduler instead
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(0, 10000, 20.0),
            create_implicit_deadline_periodic_task_h_rt(1, 5000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(2, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(3, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(4, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(5, 14000, 20.0),
            create_implicit_deadline_periodic_task_h_rt(6, 3000, 5.0)
        ]

        number_of_cores = 5
        available_frequencies = {1000, 2000, 3000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_simple_simulation_periodic_task_set_nonpreemptive_mcnaughton(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            5
        - Available frequencies (Hz):
            1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4
                    |---------|---------|---------|---------|
            Task 0  |                  job 1                |
                    |---------|---------|---------|---------|
            Task 1  |        job 2      |        job 3      |
                    |---------|---------|---------|---------|
            Task 2  |        job 4      |        job 5      |
                    |---------|---------|---------|---------|
            Task 3  |        job 6      |        job 7      |
                    |---------|---------|---------|---------|
            Task 4  |        job 8      |        job 9      |
                    |---------|---------|---------|---------|
            Task 5  |                 job 10                |
                    |---------|---------|---------|---------|
            Task 6  | job 11  | job 12  | job 13  | job 14  |
                    |---------|---------|---------|---------|
                    0         5         10        15        20
        - Commentaries for this test:
            This test is a copy of the ALECS test, using the Deutschbein CE scheduler instead
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(0, 10000, 20.0),
            create_implicit_deadline_periodic_task_h_rt(1, 5000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(2, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(3, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(4, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(5, 14000, 20.0),
            create_implicit_deadline_periodic_task_h_rt(6, 3000, 5.0)
        ]

        number_of_cores = 5
        available_frequencies = {1000, 2000, 3000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_simple_simulation_periodic_task_set_preemptive(self):
        '''
        - Preemption model:
            preemptive
        - Number of cores:
            5
        - Available frequencies (Hz):
            1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4
                    |---------|---------|---------|---------|
            Task 0  |                  job 1                |
                    |---------|---------|---------|---------|
            Task 1  |        job 2      |        job 3      |
                    |---------|---------|---------|---------|
            Task 2  |        job 4      |        job 5      |
                    |---------|---------|---------|---------|
            Task 3  |        job 6      |        job 7      |
                    |---------|---------|---------|---------|
            Task 4  |        job 8      |        job 9      |
                    |---------|---------|---------|---------|
            Task 5  |                 job 10                |
                    |---------|---------|---------|---------|
            Task 6  | job 11  | job 12  | job 13  | job 14  |
                    |---------|---------|---------|---------|
                    0         5         10        15        20
        - Commentaries for this test:
            This test is a copy of the ALECS test, using the Deutschbein CE scheduler instead
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(0, 10000, 20.0),
            create_implicit_deadline_periodic_task_h_rt(1, 5000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(2, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(3, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(4, 7000, 10.0),
            create_implicit_deadline_periodic_task_h_rt(5, 14000, 20.0),
            create_implicit_deadline_periodic_task_h_rt(6, 3000, 5.0)
        ]

        number_of_cores = 5
        available_frequencies = {1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # --------------------------------------------------------------------------
    # Using the CALECS test's partitioned task set and platform

    def test_partitioned_task_set_nonpreemptive(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            4
        - Available frequencies (Hz):
            1000, 8000
        - Task set:
            tests.schedulers._common_scheduler_tests_utils.periodic_implicit_deadline_tasks
        - Commentaries for this test:
            This test is a copy of the CALECS test, using the Deutschbein CE scheduler instead
        '''
        task_set = TaskSet(periodic_tasks=[create_implicit_deadline_periodic_task_h_rt(j, i[0], i[1]) for j, i in
                                           enumerate(periodic_implicit_deadline_tasks)],
                           sporadic_tasks=[],
                           aperiodic_tasks=[])

        number_of_cores = 4
        available_frequencies = {1000, 8000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=task_set,
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_partitioned_task_set_nonpreemptive_mcnaughton(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            4
        - Available frequencies (Hz):
            1000, 8000
        - Task set:
            tests.schedulers._common_scheduler_tests_utils.periodic_implicit_deadline_tasks
        - Commentaries for this test:
            This test is a copy of the CALECS test, using the Deutschbein CE scheduler instead
        '''
        task_set = TaskSet(periodic_tasks=[create_implicit_deadline_periodic_task_h_rt(j, i[0], i[1]) for j, i in
                                           enumerate(periodic_implicit_deadline_tasks)],
                           sporadic_tasks=[],
                           aperiodic_tasks=[])

        number_of_cores = 4
        available_frequencies = {1000, 8000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=task_set,
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_partitioned_task_set_preemptive(self):
        '''
        - Preemption model:
            preemptive
        - Number of cores:
            4
        - Available frequencies (Hz):
            1000, 1024
        - Task set:
            tests.schedulers._common_scheduler_tests_utils.periodic_implicit_deadline_tasks
        - Commentaries for this test:
            This test is a copy of the CALECS test, using the Deutschbein CE scheduler instead
        '''
        task_set = TaskSet(periodic_tasks=[create_implicit_deadline_periodic_task_h_rt(j, i[0], i[1]) for j, i in
                                           enumerate(periodic_implicit_deadline_tasks)],
                           sporadic_tasks=[],
                           aperiodic_tasks=[])

        number_of_cores = 4
        available_frequencies = {1000, 1024}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=task_set,
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # --------------------------------------------------------------------------
    # Existing scheduling point but no schedule_policy invocation because there are no active jobs

    def test_artifacts_experiment0_nonpreemptive(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1000
        - Task set:
            Task 0 : period = 15.0, WCET =  5130
	        Task 1 : period = 10.0, WCET =  4180
	        Task 2 : period =  3.0, WCET =  1227
	        Task 3 : period =  3.0, WCET =   411
	        Task 4 : period = 10.0, WCET =  1070
	        Task 5 : period = 60.0, WCET = 10080
	        Task 6 : period =  1.0, WCET =   316
	        Task 7 : period = 60.0, WCET =  6180
        - Commentaries for this test:
            In the frame 39, after executing all the jobs assigned (jobs 96 and 23), it exists an scheduling point in which all
            the cores must be left empty. Nevertheless, as there are no active jobs, the simulator will miss the invocation to
            the scheduler, so that scheduling point must be supressed of the list in order the simulation to work as expected

            NOTE: the task set used in this test has been obtained from the first experiment of the artifacts of the paper
            "Accounting for Preemption and Migration Costs in the Calculation of Hard Real-Time Cyclic Executives for MPSoCs",
            which can be found here https://ieeexplore.ieee.org/document/9807417
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(0, 5130, 15.0),
            create_implicit_deadline_periodic_task_h_rt(1, 4180, 10.0),
            create_implicit_deadline_periodic_task_h_rt(2, 1227, 3.0),
            create_implicit_deadline_periodic_task_h_rt(3, 411, 3.0),
            create_implicit_deadline_periodic_task_h_rt(4, 1070, 10.0),
            create_implicit_deadline_periodic_task_h_rt(5, 10080, 60.0),
            create_implicit_deadline_periodic_task_h_rt(6, 316, 1.0),
            create_implicit_deadline_periodic_task_h_rt(7, 6180, 60.0)
        ]

        number_of_cores = 2
        available_frequencies = {1000, 10080}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_artifacts_experiment0_nonpreemptive_mcnaughton(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1000
        - Task set:
            Task 0 : period = 15.0, WCET =  5130
	        Task 1 : period = 10.0, WCET =  4180
	        Task 2 : period =  3.0, WCET =  1227
	        Task 3 : period =  3.0, WCET =   411
	        Task 4 : period = 10.0, WCET =  1070
	        Task 5 : period = 60.0, WCET = 10080
	        Task 6 : period =  1.0, WCET =   316
	        Task 7 : period = 60.0, WCET =  6180
        - Commentaries for this test:
            In the frame 39, after executing all the jobs assigned (jobs 96 and 23), it exists an scheduling point in which all
            the cores must be left empty. Nevertheless, as there are no active jobs, the simulator will miss the invocation to
            the scheduler, so that scheduling point must be supressed of the list in order the simulation to work as expected

            NOTE: the task set used in this test has been obtained from the first experiment of the artifacts of the paper
            "Accounting for Preemption and Migration Costs in the Calculation of Hard Real-Time Cyclic Executives for MPSoCs",
            which can be found here https://ieeexplore.ieee.org/document/9807417
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(0, 5130, 15.0),
            create_implicit_deadline_periodic_task_h_rt(1, 4180, 10.0),
            create_implicit_deadline_periodic_task_h_rt(2, 1227, 3.0),
            create_implicit_deadline_periodic_task_h_rt(3, 411, 3.0),
            create_implicit_deadline_periodic_task_h_rt(4, 1070, 10.0),
            create_implicit_deadline_periodic_task_h_rt(5, 10080, 60.0),
            create_implicit_deadline_periodic_task_h_rt(6, 316, 1.0),
            create_implicit_deadline_periodic_task_h_rt(7, 6180, 60.0)
        ]

        number_of_cores = 2
        available_frequencies = {1000, 10080}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # --------------------------------------------------------------------------
    # No scheduling point at major cycle start

    def test_artifacts_experiment6_nonpreemptive(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1000
        - Task set:
        	Task 0 : period = 12.0, WCET = 4812
	        Task 1 : period = 15.0, WCET = 8445
	        Task 2 : period = 20.0, WCET = 4820
	        Task 3 : period = 30.0, WCET = 1500
	        Task 4 : period = 15.0, WCET =  675
	        Task 5 : period = 15.0, WCET = 6045
	        Task 6 : period =  2.0, WCET =  322
	        Task 7 : period = 15.0, WCET = 2040
        - Commentaries for this test:
            In the frame 0, there is no execution asssigned for any of the jobs, so that the first scheduling point does not
            match the starting of the major cycle. That's why it must be explicitly added an scheduling point at cycle 0 in
            order the simulation to work as expected

            NOTE: the task set used in this test has been obtained from the seventh experiment of the artifacts of the paper
            "Accounting for Preemption and Migration Costs in the Calculation of Hard Real-Time Cyclic Executives for MPSoCs",
            which can be found here https://ieeexplore.ieee.org/document/9807417
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(0, 4812, 12.0),
            create_implicit_deadline_periodic_task_h_rt(1, 8445, 15.0),
            create_implicit_deadline_periodic_task_h_rt(2, 4820, 20.0),
            create_implicit_deadline_periodic_task_h_rt(3, 1500, 30.0),
            create_implicit_deadline_periodic_task_h_rt(4, 675, 15.0),
            create_implicit_deadline_periodic_task_h_rt(5, 6045, 15.0),
            create_implicit_deadline_periodic_task_h_rt(6, 322, 2.0),
            create_implicit_deadline_periodic_task_h_rt(7, 2040, 15.0)
        ]

        number_of_cores = 2
        available_frequencies = {1000, 8445}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # -------------------------------------
    def test_artifacts_experiment6_nonpreemptive_mcnaughton(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1000
        - Task set:
        	Task 0 : period = 12.0, WCET = 4812
	        Task 1 : period = 15.0, WCET = 8445
	        Task 2 : period = 20.0, WCET = 4820
	        Task 3 : period = 30.0, WCET = 1500
	        Task 4 : period = 15.0, WCET =  675
	        Task 5 : period = 15.0, WCET = 6045
	        Task 6 : period =  2.0, WCET =  322
	        Task 7 : period = 15.0, WCET = 2040
        - Commentaries for this test:
            In the frame 0, there is no execution asssigned for any of the jobs, so that the first scheduling point does not
            match the starting of the major cycle. That's why it must be explicitly added an scheduling point at cycle 0 in
            order the simulation to work as expected

            NOTE: the task set used in this test has been obtained from the seventh experiment of the artifacts of the paper
            "Accounting for Preemption and Migration Costs in the Calculation of Hard Real-Time Cyclic Executives for MPSoCs",
            which can be found here https://ieeexplore.ieee.org/document/9807417
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(0, 4812, 12.0),
            create_implicit_deadline_periodic_task_h_rt(1, 8445, 15.0),
            create_implicit_deadline_periodic_task_h_rt(2, 4820, 20.0),
            create_implicit_deadline_periodic_task_h_rt(3, 1500, 30.0),
            create_implicit_deadline_periodic_task_h_rt(4, 675, 15.0),
            create_implicit_deadline_periodic_task_h_rt(5, 6045, 15.0),
            create_implicit_deadline_periodic_task_h_rt(6, 322, 2.0),
            create_implicit_deadline_periodic_task_h_rt(7, 2040, 15.0)
        ]

        number_of_cores = 2
        available_frequencies = {1000, 8445}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
        )

        # Correct execution
        assert simulation_result.have_been_scheduled
        assert simulation_result.hard_real_time_deadline_missed_stack_trace is None

    # --------------------------------------------------------------------------
    # Available frequencies are insufficient (the minimal necessary is greater)

    def test_nonpreemptive_insufficient_frequency(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |                            job 6                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it uses the paper's task set, but no frequency grater or equal than 40.0 Hz is given as available

            As it will be checked in the 'offline_stage' method, an AssertionError will be raised
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 12.0)
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30}

        try:
            simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
                tasks=TaskSet(
                    periodic_tasks=periodic_tasks,
                    aperiodic_tasks=[],
                    sporadic_tasks=[]
                ),
                aperiodic_tasks_jobs=[],
                sporadic_tasks_jobs=[],
                processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
                environment_specification=default_environment_specification(),
                simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
                scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
            )
            # Error due to no error detection
            assert False, "No assertion exception caught when it was expected"
        except AssertionError:
            # Correct error detection
            print("Assertion exception caught as expected")

    # -------------------------------------
    def test_nonpreemptive_mcnaughton_insufficient_frequency(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |                            job 6                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it uses the paper's task set, but no frequency grater or equal than 40.0 Hz is given as available

            As it will be checked in the 'offline_stage' method, an AssertionError will be raised
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 12.0)
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30}

        try:
            simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
                tasks=TaskSet(
                    periodic_tasks=periodic_tasks,
                    aperiodic_tasks=[],
                    sporadic_tasks=[]
                ),
                aperiodic_tasks_jobs=[],
                sporadic_tasks_jobs=[],
                processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
                environment_specification=default_environment_specification(),
                simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
                scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
            )
            # Error due to no error detection
            assert False, "No assertion exception caught when it was expected"
        except AssertionError:
            # Correct error detection
            print("Assertion exception caught as expected")

    # -------------------------------------
    def test_preemptive_insufficient_frequency(self):
        '''
        - Preemption model:
            preemptive
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |                            job 6                          |
                    |---------|---------|---------|---------|---------|---------|
                    0         2         4         6         8         10        12
        - Commentaries for this test:
            it uses the paper's task set, but no frequency grater or equal than 9.5 Hz is given as available

            As it will be checked in the 'offline_stage' method, an AssertionError will be raised
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 4.0),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 6.0),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 12.0),
        ]

        number_of_cores = 2
        available_frequencies = {1, 5}

        try:
            simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
                tasks=TaskSet(
                    periodic_tasks=periodic_tasks,
                    aperiodic_tasks=[],
                    sporadic_tasks=[]
                ),
                aperiodic_tasks_jobs=[],
                sporadic_tasks_jobs=[],
                processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
                environment_specification=default_environment_specification(),
                simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
                scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=True)
            )
            # Error due to no error detection
            assert False, "No assertion exception caught when it was expected"
        except AssertionError:
            # Correct error detection
            print("Assertion exception caught as expected")

    # --------------------------------------------------------------------------
    # Periods are decimal values

    def test_nonpreemptive_decimal_periods(self):
        '''
        - Preemption model:
            no preemptive (LPP solution for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |                            job 6                          |
                    |---------|---------|---------|---------|---------|---------|
                    0        1.25      2.5       3.75       5        6.25      7.5
        - Commentaries for this test:
            it uses the paper's task set, but changing the periods by decimal values; the major cycle's value is 7.5 seconds
            and the minor cycle's value is 1.25 seconds, but the proportions remain

            As decimal period values are not allowed, the method 'check_schudability' must report an error
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 2.5),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 3.75),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 7.5)
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False)
        )

        # Correct error detection
        assert simulation_result.scheduler_acceptance_error_message is not None
        print("Error detected correctly in 'check_schedulability':", simulation_result.scheduler_acceptance_error_message)

    # -------------------------------------
    def test_nonpreemptive_mcnaughton_decimal_periods(self):
        '''
        - Preemption model:
            no preemptive (McNaugthon's rule for cores assignation)
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |                            job 6                          |
                    |---------|---------|---------|---------|---------|---------|
                    0        1.25      2.5       3.75       5        6.25      7.5
        - Commentaries for this test:
            it uses the paper's task set, but changing the periods by decimal values; the major cycle's value is 7.5 seconds
            and the minor cycle's value is 1.25 seconds, but the proportions remain

            As decimal period values are not allowed, the method 'check_schudability' must report an error
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 2.5),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 3.75),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 7.5)
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=False, use_mcnaughton_rule=True)
        )

        # Correct error detection
        assert simulation_result.scheduler_acceptance_error_message is not None
        print("Error detected correctly in 'check_schedulability':", simulation_result.scheduler_acceptance_error_message)

    # -------------------------------------
    def test_preemptive_decimal_periods(self):
        '''
        - Preemption model:
            preemptive
        - Number of cores:
            2
        - Available frequencies (Hz):
            1, 5, 10, 30, 50, 100, 200, 500, 1000
        - Task set:
                      frame 1 | frame 2 | frame 3 | frame 4 | frame 5 | frame 6
                    |---------|---------|---------|---------|---------|---------|
            Task 1  |        job 1      |        job 2      |        job 3      |
                    |---------|---------|---------|---------|---------|---------|
            Task 2  |            job 4            |            job 5            |
                    |---------|---------|---------|---------|---------|---------|
            Task 3  |                            job 6                          |
                    |---------|---------|---------|---------|---------|---------|
                    0        1.25      2.5       3.75       5        6.25      7.5
        - Commentaries for this test:
            it uses the paper's task set, but changing the periods by decimal values; the major cycle's value is 7.5 seconds
            and the minor cycle's value is 1.25 seconds, but the proportions remain

            As decimal period values are not allowed, the method 'check_schudability' must report an error
        '''
        periodic_tasks = [
            create_implicit_deadline_periodic_task_h_rt(1, 20, 2.5),
            create_implicit_deadline_periodic_task_h_rt(2, 40, 3.75),
            create_implicit_deadline_periodic_task_h_rt(3, 80, 7.5)
        ]

        number_of_cores = 2
        available_frequencies = {1, 5, 10, 30, 50, 100, 200, 500, 1000}

        simulation_result, periodic_jobs, major_cycle = execute_scheduler_simulation_simple(
            tasks=TaskSet(
                periodic_tasks=periodic_tasks,
                aperiodic_tasks=[],
                sporadic_tasks=[]
            ),
            aperiodic_tasks_jobs=[],
            sporadic_tasks_jobs=[],
            processor_definition=generate_default_cpu(number_of_cores, available_frequencies),
            environment_specification=default_environment_specification(),
            simulation_options=SimulationConfiguration(id_debug=True, nonparallelization_check=True),
            scheduler=SDeutschbeinCE(activate_debug=True, preemptive_ce=True)
        )

        # Correct error detection
        assert simulation_result.scheduler_acceptance_error_message is not None
        print("Error detected correctly in 'check_schedulability':", simulation_result.scheduler_acceptance_error_message)
