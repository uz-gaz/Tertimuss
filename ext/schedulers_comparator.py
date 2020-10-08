import json
import os
import random
import time
from multiprocessing.pool import Pool
from typing import List, Tuple, Dict, Optional

import numpy

from main.core.execution_simulator.system_modeling.GlobalModel import GlobalModel
from main.core.execution_simulator.system_modeling.ThermalModelSelector import ThermalModelSelector
from main.core.execution_simulator.system_simulator.SchedulingResult import SchedulingResult
from main.core.execution_simulator.system_simulator.SystemSimulator import SystemSimulator
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.automatic_task_generator.implementations.UUniFastDiscardCycles import \
    UUniFastDiscardCycles

from main.core.problem_specification.cpu_specification.BoardSpecification import BoardSpecification
from main.core.problem_specification.cpu_specification.CoreGroupSpecification import CoreGroupSpecification
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.cpu_specification.EnergyConsumptionProperties import EnergyConsumptionProperties
from main.core.problem_specification.cpu_specification.MaterialCuboid import MaterialCuboid
from main.core.problem_specification.environment_specification.EnvironmentSpecification import EnvironmentSpecification
from main.core.problem_specification.simulation_specification.SimulationSpecification import SimulationSpecification
from main.core.problem_specification.simulation_specification.TCPNModelSpecification import TCPNModelSpecification
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.schedulers_definition.implementations.AIECS import AIECSScheduler
from main.core.schedulers_definition.implementations.RUN import RUNScheduler
from main.core.schedulers_definition.implementations.SemiPartitionedAIECS import SemiPartitionedAIECSScheduler
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler
from main.plot_generator.implementations.ContextSwitchStatistics import ContextSwitchStatistics
from main.plot_generator.implementations.ExecutionPercentageStatistics import ExecutionPercentageStatistics
from main.plot_generator.templates.AbstractResultDrawer import AbstractResultDrawer


def run_comparison(experiment_full_name: str, number_of_cpus: int, schedulers: Dict[str, AbstractScheduler],
                   metrics_to_records: Dict[str, AbstractResultDrawer], record_on_success: bool) -> Dict[str, bool]:
    """
    Run a comparison between schedulers
    :param experiment_full_name: name of the experiment, the task set should be found
                                 on ${experiment_full_name}_asks_specification.json
    :param number_of_cpus: number of cpus
    :param schedulers: schedulers to compare
    :param metrics_to_records: plots that want to record. The first element is the save prefix
    :param record_on_success: only save if all schedulers find a successfully solution
    :return:
    """

    print("Running:", experiment_full_name)

    task_set = []

    with open(experiment_full_name + "_tasks_specification.json", "r") as read_file:
        decoded_json = json.load(read_file)
        for i in decoded_json:
            task_set.append(PeriodicTask(i["worst_case_execution_time"], i["period"], i["period"], 0))

    result_list: Dict[str, Tuple[SchedulingResult, GlobalSpecification]] = {}
    success_list: Dict[str, Optional[bool]] = {}

    for scheduler_actual_name, scheduler_actual in schedulers.items():
        if not record_on_success or all([i[1] for i in success_list.items()]):
            try:
                result, global_specification, _ = create_problem_specification(task_set,
                                                                               scheduler_actual,
                                                                               number_of_cpus)
                result_list[scheduler_actual_name] = (result, global_specification)

                success_list[scheduler_actual_name] = not _have_miss_deadline(global_specification, result)

            except Exception as e:
                print("Fail for " + scheduler_actual_name)
                print(e.args)
                success_list[scheduler_actual_name] = False
        else:
            success_list[scheduler_actual_name] = None

    if not record_on_success or all([i[1] for i in success_list.items()]):
        # Save plots
        for scheduler_actual_name, (result, global_specification) in result_list.items():
            for drawer_name, drawer_type in metrics_to_records.items():
                drawer_type.plot(global_specification, result,
                                 {
                                     "save_path": experiment_full_name + "_" + scheduler_actual_name + "_" + drawer_name})

    return success_list


def _have_miss_deadline(global_specification: GlobalSpecification, scheduler_result: SchedulingResult) -> bool:
    """
         Plot task execution in each cpu
         :param global_specification: problem specification
         :param scheduler_result: result of scheduling
         """

    i_tau_disc = scheduler_result.scheduler_assignation
    frequencies = scheduler_result.frequencies

    m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

    n_periodic = len(global_specification.tasks_specification.periodic_tasks)
    n_aperiodic = len(global_specification.tasks_specification.aperiodic_tasks)

    frequencies_disc_f = numpy.concatenate(
        [numpy.repeat(i.reshape(1, -1), n_periodic + n_aperiodic, axis=0) for i in frequencies], axis=0)

    i_tau_disc = i_tau_disc * frequencies_disc_f

    hyperperiod = int(global_specification.tasks_specification.h / global_specification.simulation_specification.dt)

    ci_p_dt = [i.c for i in
               global_specification.tasks_specification.periodic_tasks]

    di_p_dt = [int(round(i.d / global_specification.simulation_specification.dt)) for i in
               global_specification.tasks_specification.periodic_tasks]

    ti_p_dt = [int(round(i.t / global_specification.simulation_specification.dt)) for i in
               global_specification.tasks_specification.periodic_tasks]

    ci_a_dt = [i.c for i in global_specification.tasks_specification.aperiodic_tasks]

    ai_a_dt = [int(round(i.a / global_specification.simulation_specification.dt)) for i in
               global_specification.tasks_specification.aperiodic_tasks]

    di_a_dt = [int(round(i.d / global_specification.simulation_specification.dt)) for i in
               global_specification.tasks_specification.aperiodic_tasks]

    i_tau_disc_accond = numpy.zeros((n_periodic + n_aperiodic, len(i_tau_disc[0])))

    for i in range(m):
        i_tau_disc_accond = i_tau_disc_accond + i_tau_disc[
                                                i * (n_periodic + n_aperiodic): (i + 1) * (
                                                        n_periodic + n_aperiodic), :]
    number_deadline_missed = 0

    for i in range(n_periodic):
        missed_deadlines = 0
        missed_deadline_jobs = []
        missed_deadline_jobs_cycles = []
        period_ranges = list(range(0, hyperperiod, ti_p_dt[i]))
        for j in range(len(period_ranges)):
            if (sum(i_tau_disc_accond[i, period_ranges[j]: period_ranges[j] + di_p_dt[i]]) *
                global_specification.simulation_specification.dt) / ci_p_dt[i] < 1.0:
                missed_deadlines = missed_deadlines + 1
                missed_deadline_jobs.append(j)
                missed_deadline_jobs_cycles.append(
                    (sum(i_tau_disc_accond[i, period_ranges[j]: period_ranges[j] + di_p_dt[i]]) *
                     global_specification.simulation_specification.dt))

        if missed_deadlines > 0:
            number_deadline_missed = number_deadline_missed + missed_deadlines

    for i in range(n_aperiodic):
        if (sum(i_tau_disc_accond[n_periodic + i, ai_a_dt[i]: di_a_dt[i]]) *
            global_specification.simulation_specification.dt) / ci_a_dt[i] < 1.0:
            number_deadline_missed = number_deadline_missed + 1

    return number_deadline_missed != 0


def create_problem_specification(tasks_set: List[PeriodicTask], scheduler: AbstractScheduler, number_of_cpus: int):
    tasks_specification: TasksSpecification = TasksSpecification(tasks_set)

    core_specification = CoreGroupSpecification(MaterialCuboid(x=10, y=10, z=2, p=2330, c_p=712, k=148),
                                                EnergyConsumptionProperties(),
                                                # [150, 400, 600, 850, 1000],
                                                [1000],
                                                number_of_cpus * [1000])

    board_specification = BoardSpecification(MaterialCuboid(x=50, y=50, z=1, p=8933, c_p=385, k=400))

    environment_specification: EnvironmentSpecification = EnvironmentSpecification(0.001, 45, 110)

    simulation_specification: SimulationSpecification = SimulationSpecification(2, 0.001, False)

    tcpn_model_specification: TCPNModelSpecification = TCPNModelSpecification(
        ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED)

    global_specification: GlobalSpecification = GlobalSpecification(tasks_specification,
                                                                    CpuSpecification(board_specification,
                                                                                     core_specification),
                                                                    environment_specification,
                                                                    simulation_specification,
                                                                    tcpn_model_specification)

    # global_model = GlobalModel(global_specification)
    global_model = None

    return SystemSimulator.simulate(global_specification, global_model, scheduler,
                                    None), global_specification, global_model


def generate_task_set(full_experiment_name: str, number_of_cpus: int, number_of_tasks: int):
    """
    Generate a random task set from the requirements and return the experiment full name
    :param experiment_name:
    :param number_of_cpus:
    :param number_of_tasks:
    :param save_path:
    :return:
    """
    u = UUniFastDiscardCycles()
    x = u.generate(
        {
            "min_period_interval": 1,
            "max_period_interval": 1,
            "number_of_tasks": number_of_tasks,
            "utilization": number_of_cpus,
            "processor_frequency": 1000,
        }

    )

    for i in range(len(x)):
        multiplier = random.choice([1, 2, 4, 5, 8, 10, 20, 40])  # randrange(1, 9)
        x[i].d = x[i].d * multiplier
        x[i].t = x[i].t * multiplier
        x[i].c = x[i].c * multiplier

    # u = UUniFastExtended()
    # x = u.generate(
    #     {
    #         "hyperperiod": 40,
    #         "number_of_tasks": number_of_tasks,
    #         "utilization": number_of_cpus,
    #         "wcet_multiple": 1,
    #         "processor_frequency": 1000,
    #     }
    # )

    tasks_definition_dict = []

    for i in x:
        tasks_definition_dict.append({
            "type": "Periodic",
            "worst_case_execution_time": i.c,
            "period": i.d
        })

    with open(full_experiment_name + "_tasks_specification.json", 'w') as f:
        json.dump(tasks_definition_dict, f, indent=4)


if __name__ == '__main__':
    total_number_of_experiments = 4
    parallel_level = 4

    first_experiment_numeration = 300

    task_number_processors: List[Tuple[int, int]] = [
        (2, 2 * 8),
        (2, 2 * 16),
        (2, 2 * 24),
        (2, 2 * 32),

        (4, 4 * 8),
        (4, 4 * 16),
        (4, 4 * 24),
        (4, 4 * 32)
    ]

    experiments_base_folder = "out/"

    # Create dir if not exist
    if not os.path.exists(experiments_base_folder):
        os.makedirs(experiments_base_folder)

    task_set_names: List[Tuple[str, int]] = []

    # Generate task sets
    for number_of_cpus, number_of_tasks in task_number_processors:
        base_folder = experiments_base_folder + str(number_of_cpus) + "/" + str(number_of_tasks) + "/"
        # Create dir if not exist
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)

        for i in range(first_experiment_numeration, first_experiment_numeration + total_number_of_experiments):
            experiment_name = base_folder + "test_" + str(i)
            generate_task_set(experiment_name, number_of_cpus, number_of_tasks)
            task_set_names.append((experiment_name, number_of_cpus))

    work_to_do: List[Tuple[str, int, Dict[str, AbstractScheduler], Dict[str, AbstractResultDrawer], bool]] = []

    # Fill work to do
    for (experiment_name, number_of_cpus) in task_set_names:
        work_to_do.append(
            (experiment_name,
             number_of_cpus,
             {
                 # "semipartitionedaiecs": SemiPartitionedAIECSScheduler(),
                 "aiecs": AIECSScheduler(),
                 "run": RUNScheduler()
             },
             {
                 "execution_percentage_statics.json": ExecutionPercentageStatistics(),
                 "context_switch_statics.json": ContextSwitchStatistics()
             },
             False
             )
        )


    def caller_function(
            arguments: Tuple[str, int, Dict[str, AbstractScheduler], Dict[str, AbstractResultDrawer], bool]):
        # run_comparison
        return run_comparison(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4])


    # Create work packages
    p = Pool(processes=parallel_level)
    success_result = p.map(caller_function, work_to_do)

    p.close()
    p.join()

    aiecs_success = sum([1 for i in success_result if i.__contains__("aiecs") and i["aiecs"]])
    run_success = sum([1 for i in success_result if i.__contains__("run") and i["run"]])

    print("AIECS SUCCESS:", aiecs_success, "/", total_number_of_experiments * len(task_number_processors))
    print("RUN SUCCESS:", run_success, "/", total_number_of_experiments * len(task_number_processors))

# if __name__ == '__main__':
#     start_time = time.perf_counter()
#     run_comparison("comparison_results/out/2/32/test_25",
#                    2,
#                    {
#                        "aiecs": AIECSScheduler()
#                        # "run": RUNScheduler()
#                    },
#                    {
#                        "execution_percentage_statics.json": ExecutionPercentageStatistics(),
#                        "context_switch_statics.json": ContextSwitchStatistics()
#                    },
#                    False)
#     end_time = time.perf_counter()
#     print("Elapsed time:", end_time - start_time)
