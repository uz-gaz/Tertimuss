import json
from typing import List, Tuple
import statistics


def do_plots():
    tests_base_names: List[Tuple[str, str]] = [("out/2/8/", "2/8"),
                                               ("out/2/16/", "2/16"),
                                               ("out/2/24/", "2/24"),
                                               ("out/2/32/", "2/32"),
                                               ("out/2/40/", "2/40"),

                                               ("out/4/16/", "4/16"),
                                               ("out/4/32/", "4/32"),
                                               ("out/4/48/", "4/48"),
                                               ("out/4/64/", "4/64"),
                                               ("out/4/80/", "4/80"),
                                               ]
    scheduler_name = "run"

    number_of_tests = 200

    # [CS ALG1, CS ALG2, CS MANDATORY, M ALG1, M ALG2]
    grouped_info: List[List[Tuple[int, int, int]]] = []

    for tests_base_name, _ in tests_base_names:
        # [CS ALG1, CS ALG2, CS MANDATORY, M ALG1, M ALG2]
        local_grouped_info: List[Tuple[int, int, int]] = []

        for i in range(number_of_tests):
            name = "test_" + str(i)
            try:
                save_path = tests_base_name
                simulation_name = name + "_"
                with open(save_path + simulation_name + scheduler_name + "_context_switch_statics.json",
                          "r") as read_file:
                    decoded_json = json.load(read_file)
                    scheduler_produced_context_switch_number_scheduler_1 = decoded_json["statics"][
                        "scheduler_produced_context_switch_number"]
                    mandatory_context_switch_number = decoded_json["statics"]["mandatory_context_switch_number"]
                    migrations_number_scheduler_1 = decoded_json["statics"]["migrations_number"]

                local_grouped_info.append((scheduler_produced_context_switch_number_scheduler_1,
                                           mandatory_context_switch_number,
                                           migrations_number_scheduler_1))
            except Exception as e:
                print("Has fail", name)
                pass
        grouped_info.append(local_grouped_info)

    # Algorithm CS / JOBS
    algorithm_cs_ratio_means = [
        statistics.mean([CS_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local]) for
        grouped_info_local in grouped_info]

    algorithm_cs_ratio_stdev = [
        statistics.pstdev([CS_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local]) for
        grouped_info_local in grouped_info]

    algorithm_cs_ratio_quantiles = [
        statistics.quantiles([CS_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local]) for
        grouped_info_local in grouped_info]

    # Algorithm M / JOBS
    algorithm_m_ratio_means = [
        statistics.mean([M_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local]) for
        grouped_info_local in grouped_info]

    algorithm_m_ratio_stdev = [
        statistics.pstdev([M_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local]) for
        grouped_info_local in grouped_info]

    algorithm_m_ratio_quantiles = [
        statistics.quantiles([M_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local]) for
        grouped_info_local in grouped_info]

    print("Statistics for context switch and migrations mean by experiment", scheduler_name)

    for experiment_name, cs_ratio_mean, cs_ratio_stdev, cs_ratio_quantiles, m_ratio_mean, m_ratio_stdev, \
        m_ratio_quantiles in zip([i[1] for i in tests_base_names], algorithm_cs_ratio_means, algorithm_cs_ratio_stdev,
                                 algorithm_cs_ratio_quantiles, algorithm_m_ratio_means, algorithm_m_ratio_stdev,
                                 algorithm_m_ratio_quantiles):
        print("\t", experiment_name)
        print("\t\t Preemption mean by experiment mean:              ", cs_ratio_mean)
        print("\t\t Preemption mean by experiment standard deviation:", cs_ratio_stdev)
        print("\t\t Preemption mean by experiment quantiles:         ", cs_ratio_quantiles)
        print("\t\t Migrations mean by experiment mean:              ", m_ratio_mean)
        print("\t\t Migrations mean by experiment standard deviation:", m_ratio_stdev)
        print("\t\t Migrations mean by experiment quantiles:         ", m_ratio_quantiles)


if __name__ == '__main__':
    do_plots()
