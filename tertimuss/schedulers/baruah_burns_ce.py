"""
This module provides the following class:
- :class:`SBaruahBurnsCE`
"""

from typing import List, Optional, Tuple, Dict, Set, Union

from ortools.linear_solver import pywraplp

import time
import math

from ..simulation_lib.schedulers_definition import CentralizedScheduler
from ..simulation_lib.system_definition import Processor, Environment, TaskSet, Job
from ..simulation_lib.system_definition.utils import calculate_major_cycle, calculate_minor_cycle


class SBaruahBurnsCE(CentralizedScheduler):
    """
    Implementation of the scheduler proposed in the paper (see references)

    It can be generated both preemptive and no-preemptive cyclic executives

    Only periodic implicit-deadline tasks are allowed

    References:
        Multi-core cyclic executives for safety-critical systems -
        Calvin Deutschbein, Tom Fleming, Alan Burns, Sanjoy Baruah
    """

    def __init__(self, activate_debug: bool, preemptive_ce: bool, use_mcnaughton_rule: bool = False) -> None:
        """
        Create an scheduler instance

        :param activate_debug:  True if want to communicate the scheduler to be in debug mode
        :param preemptive_ce: True if preemption is allowed in the schedule
        :param use_mcnaughton_rule: True if, when preemption is not allowed, want to use the McNaughton's rule for assigning
                                    the cores instead of directly using the assignation specified in the LPP solution

                                    NOTE: if preemptive_ce is True, this value is ignored (because only McNaughton's rule can
                                    be used for the assignation)
        """
        super().__init__(activate_debug)

        # Scheduling behaviour (all of them are booleans)
        self.preemptive_ce: bool = preemptive_ce
        self.use_mcnaughton_rule: bool = use_mcnaughton_rule

        # Problem related variables (all of them are integers)
        self.N: int = None
        self.m: int = None
        self.P: int = None
        self.F: int = None
        self.n: int = None
        self.number_of_frames: int = None

        # Scheduling simulation related variables
        self.scheduling_points: Dict[int, Dict[int, int]] = None
        self.cycles_to_sleep: Dict[int, int] = None

    # -----------------------------------------------------------------
    def check_schedulability(self, processor_definition: Processor,
                             environment_specification: Environment, task_set: TaskSet) \
            -> [bool, Optional[str]]:
        """
        Return true if the scheduler can be able to schedule the system. In negative case, it can return a reason.
        In example, a scheduler that only can work with periodic tasks with phase=0, can return
         [false, "Only can schedule tasks with phase=0"]

        :param environment_specification: Specification of the environment
        :param processor_definition: Specification of the cpu
        :param task_set: Tasks in the system
        :return CPU frequency
        """

        # Only 0-phase, implicit-deadline, periodic tasks are allowed
        only_0_phase = all(i.phase is None or i.phase == 0 for i in task_set.periodic_tasks)
        only_periodic_tasks = len(task_set.sporadic_tasks) + len(task_set.aperiodic_tasks) == 0
        only_implicit_deadline = all(i.relative_deadline == i.period for i in task_set.periodic_tasks)
        # Only exact values are allowed for the periods of the tasks
        only_exact_period_values = all(task.period.is_integer() for task in task_set.periodic_tasks)

        # NOTE: the LPP feasibility can only be verified by attempting to resolve it, so that checking is deferred until the
        # offline stage

        if not (only_0_phase and only_periodic_tasks and only_implicit_deadline):
            return False, "Error: Only implicit deadline, 0 phase periodic tasks are allowed"
        elif not only_exact_period_values:
            return False, "Error: Only exact period values are allowed. In order to get them, use submultiples of the time units and consider that it will directly affect to the frequency units of the results"

        # --------------------------------
        # All tests passed
        return True, None

    # -----------------------------------------------------------------
    def offline_stage(self, processor_definition: Processor,
                      environment_specification: Environment,
                      task_set: TaskSet) -> int:
        """
        Method to implement with the offline stage scheduler tasks

        :param environment_specification: Specification of the environment
        :param processor_definition: Specification of the cpu
        :param task_set: Tasks in the system
        :return CPU frequency
        """

        # Extract system's features

        # Number of cores
        number_of_cores = len(processor_definition.cores_definition)
        # Available CPU frequencies
        clock_available_frequencies = list(Set.intersection(*[i.core_type.available_frequencies for i
                                                            in processor_definition.cores_definition.values()]))

        # --------------------------------
        # Main variables definition

        # Create the variables which will be used
        self.N = len(task_set.tasks())  # number of tasks
        self.m = number_of_cores
        self.P = int(calculate_major_cycle(task_set))  # hyperperiod duration, major cycle duration
        self.F = int(calculate_minor_cycle(task_set))  # frame duration, minor cycle duration
        self.number_of_frames = self.P//self.F

        self.n = sum([int(self.P // task.period) for task in task_set.tasks()])  # number of jobs

        jobs: List[Job] = []
        id = 0
        for task in task_set.tasks():
            for activation_number in range(int(self.P // task.period)):
                jobs.append(Job(identifier=id,
                                task=task,
                                activation_time=activation_number * task.period
                                )
                            )
                id += 1
        assert(len(jobs) == self.n)

        # Auxiliar variable which allows consulting the active jobs in a concrete frame number
        jobs_in_frame: Dict[int, Set[int]] = {k: set() for k in range(self.number_of_frames)}
        for i in range(self.n):
            for k in range(int(jobs[i].activation_time//self.F), int(jobs[i].absolute_deadline//self.F)):
                jobs_in_frame[k].add(i)

        # --------------------------------
        # Solve the LP problem
        status, x, f = self.solve_lpp(jobs, jobs_in_frame)

        try:
            assert(status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE)
        except AssertionError:
            print("Error on scheduler's offline stage: the solver could not solve the linear programming problem")
            assert(False)

        # --------------------------------
        # Discretize the continuos values obtained from the LP solution
        jobs_execution_in_frame, f_discretized = (self.accumulate_discretize_lp_solution(jobs, jobs_in_frame, x, f)
                                                  if self.preemptive_ce
                                                  else self.just_discretize_lp_solution(jobs, jobs_in_frame, x, f,
                                                                                        not self.use_mcnaughton_rule))

        # --------------------------------
        # Obtain the CPUs frequency value using the discretized value of f
        minimal_frequency = f_discretized / self.F

        # Get the minimum available frequency which is greater or equal than the minimal frequency calculated
        chosen_frequency = min(filter(lambda frequency: frequency >= minimal_frequency, clock_available_frequencies),
                               default=None)
        if not chosen_frequency:
            print("Error on scheduler's offline stage: the avaliable frequencies don't fit the problem's solution requirements (it's needed a frequency greater or equal than ", minimal_frequency, " Hz)", sep='')
            assert(False)

        # Get the f value to use for obtaining the scheduling points
        f_frequency_compliant = chosen_frequency * self.F

        # <DEBUG>
        if self.is_debug:
            print("---------------------------------------")
            print("frequency :\t current = ", minimal_frequency, ",\t original = ", f / self.F, ",\t chosen = ", chosen_frequency, sep='')
            print("f         :\t current = ", f_discretized, ",\t original = ", f, ",\t chosen = ", f_frequency_compliant, sep='')
        # </DEBUG>

        if chosen_frequency != minimal_frequency:
            print("WARNING: the frequency chosen (", chosen_frequency, " Hz) is greater than the minimal necessary (", minimal_frequency, " Hz)", sep='')

        # --------------------------------
        # Apply McNaughton's rule (preemptive case) or obtain the schedule directly (no-preemptive case) depending on the
        # preemption model which was specified
        self.scheduling_points, self.cycles_to_sleep = (self.mcnaughton_assignation(jobs_execution_in_frame, f_frequency_compliant, self.preemptive_ce)
                                                        if self.preemptive_ce or self.use_mcnaughton_rule
                                                        else self.direct_assignation(jobs_execution_in_frame, f_frequency_compliant))

        # Return the frequency used to obtain the scheduling points
        return chosen_frequency

    # -----------------------------------------------------------------
    def schedule_policy(self, global_time: float, active_jobs_id: Set[int],
                        jobs_being_executed_id: Dict[int, int], cores_frequency: int,
                        cores_max_temperature: Optional[Dict[int, float]]) \
            -> Tuple[Dict[int, int], Optional[int], Optional[int]]:
        """
        Method to implement with the actual scheduler police

        :param global_time: Time in seconds since the simulation starts
        :param jobs_being_executed_id: Ids of the jobs that are currently executed on the system. The dictionary has as
         key the CPU id (it goes from 0 to number of CPUs - 1), and as value the job id.
        :param active_jobs_id: Identifications of the jobs that are currently active
         (look in :ref:..system_definition.DeadlineCriteria for more info) and can be executed.
        :param cores_frequency: Frequencies of cores on the scheduler invocation in Hz.
        :param cores_max_temperature: Max temperature of each core. The dictionary has as
         key the CPU id, and as value the temperature in Kelvin degrees.
        :return: Tuple of [
         Jobs CPU assignation. The dictionary has as key the CPU id, and as value the job id,
         Cycles to execute until the next invocation of the scheduler. If None, it won't be executed until a system
         event trigger its invocation,
         CPU frequency. If None, it will maintain the last used frequency (cores_frequency)
        ]
        """

        # Obtain the current cycle's number
        current_cycle = round(global_time * cores_frequency) % round(self.P * cores_frequency)

        return self.scheduling_points[current_cycle], self.cycles_to_sleep[current_cycle], None

    # -----------------------------------------------------------------
    def on_major_cycle_start(self, global_time: float) -> bool:
        """
        On new major cycle start event

        :param global_time: Time in seconds since the simulation starts
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """

        # Call to the scheduler now, and then all the schedule will be based on delays (until the following major cycle
        # starting)
        return True

    # -----------------------------------------------------------------
    def on_jobs_activation(self, global_time: float, activation_time: float,
                           jobs_id_tasks_ids: List[Tuple[int, int]]) -> bool:
        """
        Method to implement with the actual on job activation scheduler police.
        This method is the recommended place to detect the arrival of an aperiodic or sporadic task.

        :param jobs_id_tasks_ids: List[Identification of the job that have been activated,
         Identification of the task which job have been activated]
        :param global_time: Actual time in seconds since the simulation starts
        :param activation_time: Time where the activation was produced (It can be different from the global_time in the
         case that it doesn't adjust to a cycle end)
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """

        # No call to the scheduler needed, because all the schedule has been made offline
        return False

    # -----------------------------------------------------------------
    def on_jobs_deadline_missed(self, global_time: float, jobs_id: List[int]) -> bool:
        """
         Method to implement with the actual on aperiodic arrive scheduler police

         :param jobs_id: Identification of the jobs that have missed the deadline
         :param global_time: Time in seconds since the simulation starts
         :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
         """

        # This should never happen
        print("Error on scheduler's simulation stage: the jobs", jobs_id, "didn't finish before their deadline")
        assert(False)
        return False

    # -----------------------------------------------------------------
    def on_job_execution_finished(self, global_time: float, jobs_id: List[int]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police

        :param jobs_id: Identification of the job that have finished its execution
        :param global_time: Time in seconds since the simulation starts
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """

        # No call to the scheduler needed, because all the schedule has been made offline
        return False

    # ----------------------------------------------------------------------------------------------------------------------------------
    # AUXILIAR METHODS

    def solve_lpp(self, jobs: List[Job], jobs_in_frame: Dict[int, Set[int]]) \
            -> Tuple[int, Optional[Tuple[Dict[Tuple[int, int, int], float], float]]]:
        """
        Solves either the linear programming or the mixed integer linear programming problem

        :param jobs: list of jobs to schedule
        :param jobs_in_frame: dictionary which associates each frame with the jobs active in it
        :return: 1 -> the status returned by the solver
                 2 -> a dictionary which associates to an integer tuple (i,j,k) the x_ijk LP variable's value
                      in the solution
                 3 -> the f LP variable's value in the solution
        """

        # --------------------------------
        # LP PROBLEM DEFINITION

        # Create the linear solver with the proper backend
        solver = pywraplp.Solver.CreateSolver('GLOP') if self.preemptive_ce else pywraplp.Solver.CreateSolver('SCIP')

        # ----------------------
        # Declare the variables

        # Create variables related to scheduling
        x = {}
        for i in range(self.n):
            for j in range(self.m):
                for k in range(int(jobs[i].activation_time//self.F), int(jobs[i].absolute_deadline//self.F)):
                    x[(i, j, k)] = (solver.NumVar(0, 1, "x_" + str(i+1) + "_" + str(j+1) + "_" + str(k+1))
                                    if self.preemptive_ce
                                    else solver.IntVar(0, 1, "x_" + str(i+1) + "_" + str(j+1) + "_" + str(k+1)))
        assert(solver.NumVariables() == self.N * self.m * self.number_of_frames)
        # <DEBUG>
        if self.is_debug:
            self.__print_variables(x, self.n)
            print("---------------------------------------")
        # </DEBUG>

        # Create variable related to objective function
        f = solver.NumVar(0, solver.infinity(), "f")

        # ----------------------
        # Declare the constraints

        # First constraint: each job must receive the required amount of execution
        for i in range(self.n):
            solver.Add(sum([sum([x[(i, j, k)]
                            for k in range(int(jobs[i].activation_time//self.F), int(jobs[i].absolute_deadline//self.F))])
                            for j in range(self.m)]) == 1)
        assert(solver.NumConstraints() == self.n)

        # Second constraint: each processor may be assigned no more than f units of execution during each minor cycle
        for j in range(self.m):
            for k in range(self.number_of_frames):
                solver.Add(sum([x[(i, j, k)] * jobs[i].execution_time for i in jobs_in_frame[k]]) <= f)
        assert(solver.NumConstraints() == (self.n + self.m * self.number_of_frames))

        # Third constraint: each job may be assigned no more than f units of execution during each minor cycle
        if self.preemptive_ce:  # only defined if preemption is allowed
            for i in range(self.n):
                for k in range(int(jobs[i].activation_time//self.F), int(jobs[i].absolute_deadline//self.F)):
                    solver.Add(sum([x[(i, j, k)] * jobs[i].execution_time for j in range(self.m)]) <= f)
            assert(solver.NumConstraints() == (self.n + (self.m + self.N) * self.number_of_frames))

        # <DEBUG>
        if self.is_debug:
            self.__print_constraints(solver.constraints(), x, f)
            print("---------------------------------------")
        # </DEBUG>

        # ----------------------
        # Declare the objective function

        solver.Minimize(f)

        # --------------------------------
        # LP PROBLEM SOLVING

        start = time.time()
        status = solver.Solve()
        end = time.time()

        # <DEBUG>
        if self.is_debug:
            if status == solver.OPTIMAL:
                print('Optimal solution was found.')
            elif status == solver.FEASIBLE:
                print('A potentially suboptimal solution was found.')
            else:
                print('The solver could not solve the problem.')

            print("Time elapsed =", end-start, "seconds")
            print("---------------------------------------")
        # </DEBUG>

        # --------------------------------
        f_solution = f.SolutionValue()
        x_solution: Dict[Tuple[int, int, int], float] = {}
        for i_j_k in x.keys():
            x_solution[i_j_k] = x[i_j_k].SolutionValue()

        # <DEBUG>
        if self.is_debug:
            self.__print_lp_solution(x_solution, f_solution)
            print("---------------------------------------")
        # </DEBUG>

        return status, x_solution, f_solution

    # -----------------------------------------------------------------
    def accumulate_discretize_lp_solution(self, jobs: List[Job], jobs_in_frame: Dict[int, Set[int]],
                                          x: Dict[Tuple[int, int, int], float], f: float) \
            -> Tuple[List[Dict[int, int]], int]:
        """
        Accumulates the amount of execution assigned to each job during each frame in the LP's solution and converts it into a
        discrete value, guaranteeing the LP constraints satisfaction with that exact values

        NOTE: this method will only be invoked for preemptive cyclic executives

        :param jobs: list of jobs to schedule
        :param jobs_in_frame: dictionary which associates each frame with the jobs active in it
        :param x: a dictionary which associates to an integer tuple (i,j,k) the x_ijk LP variable's value in the solution
        :param f: the f LP variable's value in the solution
        :return: 1 -> a list of dictionaries, one per each frame. Each dictionary has as keys the jobs identifiers which must
                      be executed in that frame, and as value the discretized amount of execution which each one has assigned
                 2 -> the result of discretizing the value of the f variable of the LP
        """

        # As both the execution assigned to each job and the f value must be in cycles, they are initially obtained as the ceil
        # of the floating values, and then the constraints are checked with them
        # If a f value satisfies the constraints, a greater one will too, so the adjustments consists of increasing the value
        # of f
        # The greatest the WCET of the tasks is, the least is the error between the LP solution and the result of the
        # discretization

        f_discretized = math.ceil(f)
        jobs_execution_in_frame: List[Dict[int, int]] = [dict() for frame in range(self.number_of_frames)]

        # Each entry i has assigned the execution which still has to be assigned to job i
        not_assigned_execution: Dict[int, int] = {job.identifier: job.execution_time for job in jobs}

        # Precalculate the error accumulated in each frame when the ceil is taken as the discretization of the jobs assignation
        jobs_execution_ceil: Dict[Tuple[int, int], int] = dict()
        error_per_frame: Dict[int, float] = {k: 0.0 for k in range(self.number_of_frames)}
        for k in range(self.number_of_frames):
            for i in jobs_in_frame[k]:
                # Calculate both the decimal and the ceil value
                job_execution = sum([x[(i, j, k)] * jobs[i].execution_time for j in range(self.m)])
                job_execution_ceil = math.ceil(job_execution)
                # Accumuate the difference to the error for this frame
                error_per_frame[k] += abs(job_execution - job_execution_ceil)
                # Store the ceil value to use it later
                jobs_execution_ceil[(i, k)] = job_execution_ceil

        # For each frame in increasing order of error when taking the ceil as discretization
        for k in sorted(error_per_frame, key=error_per_frame.get):
            for i in jobs_in_frame[k]:
                job_execution = jobs_execution_ceil[(i, k)]
                # Assign as execution only the time it keeps to be executed
                if job_execution > not_assigned_execution[jobs[i].identifier]:
                    job_execution = not_assigned_execution[jobs[i].identifier]
                not_assigned_execution[jobs[i].identifier] -= job_execution
                # Ensure the third constraint is still satisfied by incrementing the value of f
                if job_execution > f_discretized:
                    f_discretized += (job_execution - f_discretized)
                assert(job_execution <= f_discretized)
                # Add the job to the frame only if it has execution time assigned in it
                if job_execution != 0:
                    jobs_execution_in_frame[k][i] = job_execution
        for yet_not_assigned in not_assigned_execution.values():
            assert(yet_not_assigned == 0)

        for k in range(self.number_of_frames):
            # Ensure the second constraint is still satisfied by incrementing the value of f
            jobs_execution = sum(jobs_execution_in_frame[k].values())
            if jobs_execution > self.m * f_discretized:
                f_discretized += (jobs_execution - self.m * f_discretized)
            assert(jobs_execution <= self.m * f_discretized)

        for job in jobs:
            # Ensure the first constraint is satisfied
            execution_assigned_to_job = sum([jobs_execution_in_frame[k][job.identifier]
                                             if job.identifier in jobs_execution_in_frame[k]
                                             else 0
                                             for k in range(self.number_of_frames)])
            # <DEBUG>
            if self.is_debug:
                print("j", job.identifier+1, ":\t current = ", execution_assigned_to_job, ",\t original = ", job.execution_time, sep='')
            # </DEBUG>
            assert(execution_assigned_to_job == job.execution_time)

        # <DEBUG>
        if self.is_debug:
            print("f :\t current = ", f_discretized, ",\t original = ", f, sep='')
            print("---------------------------------------")
            self.__print_lp_solution_after_accumulation_discretization(jobs_execution_in_frame, f_discretized)
        # </DEBUG>

        return jobs_execution_in_frame, f_discretized

    # -----------------------------------------------------------------
    def just_discretize_lp_solution(self, jobs: List[Job], jobs_in_frame: Dict[int, Set[int]],
                                    x: Dict[Tuple[int, int, int], float], f: float, keep_cores_assignation: bool) \
            -> Tuple[Union[List[Dict[int, List[Tuple[int, int]]]], List[Dict[int, int]]], int]:
        """
        Discretizes the amount of execution assigned to each job during each frame in the LP solution, and allows keeping also
        the core number to which they were assigned

        NOTE: this method will only be invoked for no-preemptive cyclic executives

        :param jobs: list of jobs to schedule
        :param jobs_in_frame: dictionary which associates each frame with the jobs active in it
        :param x: a dictionary which associates to an integer tuple (i,j,k) the x_ijk LP variable's value in the solution
        :param f: the f LP variable's value in the solution
        :param keep_cores_assignation: True if want to keep the core number to which each job was assigned in the LPP solution
        :return: 1 -> if keep_cores_assignation is True:
                      a list of dictionaries, one per each frame. Each dictionary has as keys the available cores, and as value
                      a list of tuples; the first element of the tuple is a number of job which will be executed in that core
                      during that frame, and the second is the discretized amount of execution which that job has assigned
                      (which will be the whole execution of the job, because preemption is not allowed)
                      otherwise:
                      a list of dictionaries, one per each frame. Each dictionary has as keys the jobs identifiers which must
                      be executed in that frame, and as value the discretized amount of execution which each one has assigned

                      NOTE: if keep_cores_assignation is False, the return type is exactly the same than the
                      "accumulate_discretize_lp_solution" method's, and their values are exchangables
                 2 -> the result of discretizing the value of the f variable of the LP
        """

        f_discretized = math.ceil(f)  # f should be already an exact value
        if keep_cores_assignation:
            jobs_execution_in_frame: List[Dict[int, List[Tuple[int, int]]]] = [{core: list()
                                                                                for core in range(self.m)}
                                                                               for frame in range(self.number_of_frames)]
        else:
            jobs_execution_in_frame: List[Dict[int, int]] = [dict() for frame in range(self.number_of_frames)]

        for frame in range(self.number_of_frames):
            for core in range(self.m):
                if keep_cores_assignation:
                    jobs_execution: List[Tuple[int, int]] = list()
                for job in jobs_in_frame[frame]:
                    if x[(job, core, frame)]:
                        if keep_cores_assignation:
                            jobs_execution.append((job, jobs[job].execution_time))
                        else:
                            jobs_execution_in_frame[frame][job] = jobs[job].execution_time
                if keep_cores_assignation:
                    jobs_execution_in_frame[frame][core] = jobs_execution

        # <DEBUG>
        if self.is_debug:
            print("f :\t current = ", f_discretized, ",\t original = ", f, sep='')
            print("---------------------------------------")
            if keep_cores_assignation:
                self.__print_lp_solution_after_discretization(jobs_execution_in_frame, f_discretized)
            else:
                self.__print_lp_solution_after_accumulation_discretization(jobs_execution_in_frame, f_discretized)
        # </DEBUG>

        return jobs_execution_in_frame, f_discretized

    # -----------------------------------------------------------------
    def mcnaughton_assignation(self, jobs_execution_in_frame: List[Dict[int, int]], f: int, preemption_allowed: bool) \
            -> Tuple[Dict[int, Dict[int, int]], Dict[int, int]]:
        """
        Calculates the scheduling points and the amount of cycles that the scheduler must sleep between them, using for it the
        McNaughton's rule over the amount of execution assigned to each job during each frame

        NOTE: this method will be invoked for both preemptive and no-preemptive cyclic executives

        :param jobs_execution_in_frame: a list of dictionaries, one per each frame. Each dictionary has as keys the jobs
                                        identifiers which must be executed in that frame, and as value the discretized amount
                                        of execution which each one has assigned
        :param f: the result of discretizing the value of the f variable of the LP
        :param preemption_allowed: True if job's execution can be splitted between multiple cores during the frame
        :return: 1 -> the scheduling points (a dictionary which has as key the number of cycle in the hyper-period and as
                      value another dictionary which has as key the number of core and as value the identifier of the job
                      which has to be executed there until the next scheduling point)
                 2 -> the number of cycles that the scheduler must sleep after each scheduling point (a dictionary which
                      has as key the number of cycle in the hyper-period and as value the number of cycles which the
                      scheduler has to sleep until its next activation)
        """

        # Dictionary which has as key the number of cycle in the hyper-period and as value another dictionary which has as key
        # the number of core and as value the identifier of the job which has to be executed there until the next scheduling
        # point
        scheduling_points: Dict[int, Dict[int, int]] = {}

        # Dictionary which has as key the number of cycle in the hyper-period and as value the number of cycles which the
        # scheduler has to sleep until its next activation
        cycles_to_sleep: Dict[int, int] = {}

        # For each frame (as the paper states)
        for frame_index, jobs_execution in enumerate(jobs_execution_in_frame):
            # The current frame occupies the interval [frame_beginning, frame_ending)
            frame_beginning = f * frame_index
            frame_ending = f * (frame_index + 1)
            assignation_border = frame_beginning
            assignation_processor = 0
            # For each job that receives any execution in this frame (ordered arbitrarily)
            for job, job_execution in jobs_execution.items():
                # Check whether the job fits into the core
                if frame_ending - assignation_border < job_execution:
                    if assignation_border not in scheduling_points:
                        scheduling_points[assignation_border] = {}
                    # If preemtion is allowed, the job's execution is splited between the current processor and the following
                    if preemption_allowed:
                        scheduling_points[assignation_border][assignation_processor] = job
                        if frame_ending not in scheduling_points:
                            scheduling_points[frame_ending] = {}
                        scheduling_points[frame_ending][assignation_processor] = None  # necessary for knowing that the core is left empty
                    # If preemtion is not allowed, the job's execution is entirely deferred to the following processor
                    else:
                        scheduling_points[assignation_border][assignation_processor] = None  # necessary for knowing that the core is left empty
                    # Update the assignation variables properly
                    if preemption_allowed:
                        # Job execution only must be updated if its execution has been splitted
                        job_execution -= (frame_ending - assignation_border)
                    assignation_border = frame_beginning
                    assignation_processor += 1
                # The job fits into the current processor
                new_assignation_border = assignation_border + job_execution
                if assignation_border not in scheduling_points:
                    scheduling_points[assignation_border] = {}
                scheduling_points[assignation_border][assignation_processor] = job
                if new_assignation_border not in scheduling_points:
                    scheduling_points[new_assignation_border] = {}
                scheduling_points[new_assignation_border][assignation_processor] = None  # necessary for knowing that the core is left empty
                # Update the assignation variables properly
                # # Update the assignation border
                assignation_border = new_assignation_border if new_assignation_border != frame_ending else frame_beginning
                # # Increase the processor number if the current has been filled
                if assignation_border == frame_beginning:
                    assignation_processor += 1

        # Complete the scheduling points, calculate the cycles to sleep between them and remove the Nones introduced
        cycles_to_sleep = self.complete_scheduling_points(scheduling_points, f)

        return scheduling_points, cycles_to_sleep

    # -----------------------------------------------------------------
    def direct_assignation(self, jobs_execution_in_frame: List[Dict[int, List[Tuple[int, int]]]], f: int) \
            -> Tuple[Dict[int, Dict[int, int]], Dict[int, int]]:
        """
        Calculates the scheduling points and the amount of cycles that the scheduler must sleep between them, placing in each
        one of the cores the jobs which were assigned to it during each frame

        NOTE: this method will only be invoked for no-preemptive cyclic executives

        :param jobs_execution_in_frame: a list of dictionaries, one per each frame. Each dictionary has as keys the available
                                        cores, and as value a list of tuples; the first element of the tuple is a number of job
                                        which will be executed in that core during that frame, and the second is the
                                        discretized amount of execution which that job has assigned (which will be the whole
                                        execution of the job, because preemption is not allowed)
        :param f: the result of discretizing the value of the f variable of the LP
        :return: 1 -> the scheduling points (a dictionary which has as key the number of cycle in the hyper-period and as
                      value another dictionary which has as key the number of core and as value the identifier of the job
                      which has to be executed there until the next scheduling point)
                 2 -> the number of cycles that the scheduler must sleep after each scheduling point (a dictionary which
                      has as key the number of cycle in the hyper-period and as value the number of cycles which the
                      scheduler has to sleep until its next activation)
        """

        # Dictionary which has as key the number of cycle in the hyper-period and as value another dictionary which has as key
        # the number of core and as value the identifier of the job which has to be executed there until the next scheduling
        # point
        scheduling_points: Dict[int, Dict[int, int]] = {}

        # Dictionary which has as key the number of cycle in the hyper-period and as value the number of cycles which the
        # scheduler has to sleep until its next activation
        cycles_to_sleep: Dict[int, int] = {}

        # For each frame (as the paper states)
        for frame_index, jobs_execution_per_core in enumerate(jobs_execution_in_frame):
            # For each one of the cores
            for assignation_processor, jobs_assigned in jobs_execution_per_core.items():
                # The current frame occupies the interval [frame_beginning, frame_ending)
                frame_beginning = f * frame_index
                assignation_border = frame_beginning
                # For each job that receives it's execution in this frame in that core
                for job, job_execution in jobs_assigned:
                    # Schedule the job into this processor
                    new_assignation_border = assignation_border + job_execution
                    if assignation_border not in scheduling_points:
                        scheduling_points[assignation_border] = {}
                    scheduling_points[assignation_border][assignation_processor] = job
                    if new_assignation_border not in scheduling_points:
                        scheduling_points[new_assignation_border] = {}
                    scheduling_points[new_assignation_border][assignation_processor] = None  # necessary for knowing that the core is left empty
                    # Update the assignation border
                    assignation_border = new_assignation_border

        # Complete the scheduling points, calculate the cycles to sleep between them and remove the Nones introduced
        cycles_to_sleep = self.complete_scheduling_points(scheduling_points, f)

        return scheduling_points, cycles_to_sleep

    # -----------------------------------------------------------------
    def complete_scheduling_points(self, scheduling_points: Dict[int, Dict[int, int]], f: int) \
            -> Dict[int, int]:
        """
        Completes the scheduling points (calculates the jobs which must still being executing in each one of the no specified
        cores and removes the cores which has None as job assigned) and calculates the cycles to sleep between consecutive
        scheduling points

        NOTE: this method will be invoked for both preemptive and no-preemptive cyclic executives

        :param scheduling_points: the partially calculated scheduling points (a dictionary which has as key the number of cycle
                                  in the hyper-period and as value another dictionary which has as key the number of core and
                                  as value the identifier of the job which has to be executed there until the next scheduling
                                  point)

                                  Note that this parameter is passed as a reference, so that its value will be modified by this
                                  method and returned as another result of it
        :param f: the result of discretizing the value of the f variable of the LP
        :return: the number of cycles that the scheduler must sleep after each scheduling point (a dictionary which has as key
                 the number of cycle in the hyper-period and as value the number of cycles which the scheduler has to sleep
                 until its next activation)
        """

        # Dictionary which has as key the number of cycle in the hyper-period and as value the number of cycles which the
        # scheduler has to sleep until its next activation
        cycles_to_sleep: Dict[int, int] = {}

        # Obtain a list with the scheduling points sorted in increasing order
        scheduling_points_cycles = sorted(scheduling_points.keys())

        # Complete the scheduling points including all the processors assignation in each one of them
        # # Complete the first scheduling point to have it as reference
        point = scheduling_points_cycles[0]
        for core in range(self.m):
            if core not in scheduling_points[point]:
                # Assign no job to the core
                scheduling_points[point][core] = None
        # # Complete the rest of the scheduling points taking the previous as reference
        for index in range(1, len(scheduling_points_cycles)):
            point = scheduling_points_cycles[index]
            for core in range(self.m):
                if core not in scheduling_points[point]:
                    # Assign the same job which was assigned to this core in the previous scheduling point
                    scheduling_points[point][core] = scheduling_points[scheduling_points_cycles[index-1]][core]

        # Calculate the number of cycles that the scheduler has to sleep between the scheduling points
        for index in range(1, len(scheduling_points_cycles)+1):
            cycles_to_sleep[scheduling_points_cycles[index-1]] = (scheduling_points_cycles[index] - scheduling_points_cycles[index-1]
                                                                  if index != len(scheduling_points_cycles)
                                                                  else f * self.number_of_frames - scheduling_points_cycles[index-1])
        for point in cycles_to_sleep:
            assert(point + cycles_to_sleep[point] in scheduling_points or point + cycles_to_sleep[point] == f * self.number_of_frames)

        # Remove the last scheduling point from both dictionaries, because it will never be used (it coincides whith the major
        # cycle start, so 0 must be used instead)
        if f * self.number_of_frames in scheduling_points:
            scheduling_points.pop(f * self.number_of_frames)
        if f * self.number_of_frames in cycles_to_sleep:
            cycles_to_sleep.pop(f * self.number_of_frames)

        # Make the last cycle's sleep time Tertimuss-compatible, assigning None to it. This way, the next invocation of the
        # "schedule_policy" will be made by "on_major_cycle_start"
        if f * self.number_of_frames in scheduling_points_cycles:
            cycles_to_sleep[scheduling_points_cycles[-2]] = None
        else:
            cycles_to_sleep[scheduling_points_cycles[-1]] = None

        # Make the scheduling points Tertimuss-compatible, deleting from them the CPUs which have None as job assigned
        for point in scheduling_points:
            for core in range(self.m):
                if scheduling_points[point][core] is None:
                    scheduling_points[point].pop(core)

        # <DEBUG>
        if self.is_debug:
            print("---------------------------------------")
            self.__print_scheduling_points(scheduling_points)
            print("---------------------------------------")
            self.__print_cycles_to_sleep(cycles_to_sleep)
        # </DEBUG>

        return cycles_to_sleep

    # ----------------------------------------------------------------------------------------------------------------------------------
    # DEBUG-RELATED METHODS

    def __print_variables(self, x: Dict[Tuple[int, int, int], pywraplp.Variable], n: int):
        variables_per_job = [[] for _ in range(n)]
        # Fill the jobs list
        for _, xijk in x.items():
            variable = xijk.name()
            variables_per_job[int(variable[variable.index('_', 1)+1: variable.index('_', 2)])-1].append(variable)
        # Print the variables related to each job
        for job, variables in enumerate(variables_per_job):
            string = str(job+1) + ": "
            for variable in variables_per_job[job]:
                string += variable + ", "
            # Print the string removing the last ", "
            print(string[:-2])

    def __print_constraints(self, constraints: List[pywraplp.Constraint], x: Dict[Tuple[int, int, int], pywraplp.Variable],
                            f: pywraplp.Variable):
        for index, constraint in enumerate(constraints):
            string = str()
            # Print left side of the inequation
            for _, xijk in x.items():
                # Print x_i_j_k variable only if it's set
                if constraint.GetCoefficient(xijk) != 0:
                    string += (xijk.name()
                               if constraint.GetCoefficient(xijk) == 1.0
                               else str(constraint.GetCoefficient(xijk)) + "·" + xijk.name())
                    string += " + "
            # Print right side of the inequation
            # # Remove the last plus sign deleting the last two characters of the string
            string = string[:-2]
            # # Check the inequation sign and the upper bound of the constraint (whether it's the f variable or 1)
            if constraint.GetCoefficient(f) == 0:
                # The relation is '=' and the upper bound is 1 (and the lower bound)
                string += "= 1"
            else:  # constraint.GetCoefficient(f) == -1.0
                # The relation is '≤' and the upper bound is the f variable
                string += "≤ " + f.name()
            # Print the constraint and its number
            print(index+1, ": ", string, sep='')

    def __print_lp_solution(self, x: Dict[Tuple[int, int, int], float], f: float):
        print("f =", f)
        for i_j_k in x.keys():
            print("x_", i_j_k[0]+1, "_", i_j_k[1]+1, "_", i_j_k[2]+1, " = ", x[i_j_k], sep='')

    def __print_lp_solution_after_accumulation_discretization(self, jobs_execution_in_frame: List[Dict[int, int]], f: int):
        print("f =", f)
        for frame_number, jobs_execution in enumerate(jobs_execution_in_frame):
            print("Frame ", frame_number+1, ":", sep='')
            for job, execution_time in jobs_execution.items():
                print("\tJob ", job+1, " -> ", execution_time, " cycles", sep='')

    def __print_lp_solution_after_discretization(self, jobs_execution_in_frame: List[Dict[int, List[Tuple[int, int]]]],
                                                 f: int):
        print("f =", f)
        for frame_number, jobs_execution_per_core in enumerate(jobs_execution_in_frame):
            print("Frame ", frame_number+1, ":", sep='')
            for core, jobs_assigned in jobs_execution_per_core.items():
                print("\tCore ", core+1, ":", sep='')
                for job, execution_time in jobs_assigned:
                    print("\t\tJob ", job+1, " -> ", execution_time, " cycles", sep='')

    def __print_scheduling_points(self, scheduling_points: Dict[int, Dict[int, int]]):
        for cycle, cores_assignation in sorted(scheduling_points.items()):
            print("Cycle ", cycle, ":", sep='')
            for core, job_id in sorted(cores_assignation.items()):
                print("\tCPU ", core+1, " -> job ", job_id+1, sep='')

    def __print_cycles_to_sleep(self, cycles_to_sleep: Dict[int, int]):
        for cycle, cycles_sleeping in sorted(cycles_to_sleep.items()):
            print("In cycle ", cycle, " -> sleep for ", cycles_sleeping, " cycles", sep='')
