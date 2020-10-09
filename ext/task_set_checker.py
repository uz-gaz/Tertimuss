import json

from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask


def check_if_has_full_utilization(experiment_full_name: str, frequency: int, num_of_cpus: int,
                                  hyperperiod: float) -> bool:
    task_set = []

    with open(experiment_full_name + "_tasks_specification.json", "r") as read_file:
        decoded_json = json.load(read_file)
        for i in decoded_json:
            task_set.append(PeriodicTask(i["worst_case_execution_time"], i["period"], i["period"], 0))

    max_period = hyperperiod

    max_cycles = round(frequency * max_period)

    total_cycles = [i.c * round(max_period / i.d) for i in task_set]

    task_utilization_excess = any([i > max_cycles for i in total_cycles])

    total_utilized_cycles = sum(total_cycles)

    zero_or_negative_cycles_in_task_set = any([i.c <= 0 for i in task_set])

    if task_utilization_excess:
        print("Excess of utilization of task in task-set", experiment_full_name)
        return False
    elif total_utilized_cycles < max_cycles * num_of_cpus:
        print("Infra-utilized task-set", experiment_full_name)
        return False
    elif total_utilized_cycles > max_cycles * num_of_cpus:
        print("Excess of utilization in task-set", experiment_full_name)
        return False
    elif zero_or_negative_cycles_in_task_set:
        print("Task set have some task with zero or negative cycles number", experiment_full_name)
        return False
    else:
        return True


if __name__ == '__main__':
    num_ok_experiments = 0

    for j in range(200):
        experiment_name = "./out/4/80/test_" + str(j)
        num_cpus = 4
        frequency_actual = 1000
        hyperperiod_actual = 60
        result = check_if_has_full_utilization(experiment_name, frequency_actual, num_cpus, hyperperiod_actual)
        if result:
            num_ok_experiments = num_ok_experiments + 1

    print("Num ok experiments", num_ok_experiments, "/", 200)
