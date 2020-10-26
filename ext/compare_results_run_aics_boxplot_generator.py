import csv
import json
from typing import List, Tuple

import scipy.stats
import matplotlib.pyplot as plt


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
    scheduler_1_name = "aiecs"
    scheduler_2_name = "run"

    number_of_tests = 200

    # [CS ALG1, CS ALG2, CS MANDATORY, M ALG1, M ALG2]
    grouped_info: List[List[Tuple[int, int, int, int, int]]] = []

    for tests_base_name, _ in tests_base_names:
        # [CS ALG1, CS ALG2, CS MANDATORY, M ALG1, M ALG2]
        local_grouped_info: List[Tuple[int, int, int, int, int]] = []

        for i in range(number_of_tests):
            name = "test_" + str(i)
            try:
                save_path = tests_base_name
                simulation_name = name + "_"
                with open(save_path + simulation_name + scheduler_1_name + "_context_switch_statics.json",
                          "r") as read_file:
                    decoded_json = json.load(read_file)
                    scheduler_produced_context_switch_number_scheduler_1 = decoded_json["statics"][
                        "scheduler_produced_context_switch_number"]
                    mandatory_context_switch_number = decoded_json["statics"]["mandatory_context_switch_number"]
                    migrations_number_scheduler_1 = decoded_json["statics"]["migrations_number"]

                with open(save_path + simulation_name + scheduler_2_name + "_context_switch_statics.json",
                          "r") as read_file:
                    decoded_json = json.load(read_file)
                    scheduler_produced_context_switch_number_scheduler_2 = decoded_json["statics"][
                        "scheduler_produced_context_switch_number"]
                    migrations_number_scheduler_2 = decoded_json["statics"]["migrations_number"]

                local_grouped_info.append((scheduler_produced_context_switch_number_scheduler_1,
                                           scheduler_produced_context_switch_number_scheduler_2,
                                           mandatory_context_switch_number,
                                           migrations_number_scheduler_1, migrations_number_scheduler_2))
            except Exception as e:
                print("Has fail", name)
                pass
        grouped_info.append(local_grouped_info)

    # Algorithm 1 CS / Mandatory CS
    algorithm_1_cs_ratio = [[CS_ALG1 / CS_MANDATORY for (CS_ALG1, CS_ALG2, CS_MANDATORY, M_ALG1, M_ALG2)
                             in grouped_info_local] for grouped_info_local in grouped_info]

    # Algorithm 2 CS / Mandatory CS
    algorithm_2_cs_ratio = [[CS_ALG2 / CS_MANDATORY for (CS_ALG1, CS_ALG2, CS_MANDATORY, M_ALG1, M_ALG2)
                             in grouped_info_local] for grouped_info_local in grouped_info]

    # Algorithm 1 CS / Mandatory CS
    algorithm_1_m_ratio = [[M_ALG1 / CS_MANDATORY for (CS_ALG1, CS_ALG2, CS_MANDATORY, M_ALG1, M_ALG2)
                            in grouped_info_local] for grouped_info_local in grouped_info]

    # Algorithm 2 CS / Mandatory CS
    algorithm_2_m_ratio = [[M_ALG2 / CS_MANDATORY for (CS_ALG1, CS_ALG2, CS_MANDATORY, M_ALG1, M_ALG2)
                            in grouped_info_local] for grouped_info_local in grouped_info]

    # CS
    fig1, ax1 = plt.subplots()
    ax1.set_title("Boxplot " + scheduler_1_name + " produced (extra) context switch / JOB")
    ax1.boxplot(algorithm_1_cs_ratio)

    ax1.set_xticklabels([i[1] for i in tests_base_names])

    plt.show()

    fig1, ax1 = plt.subplots()
    ax1.set_title("Boxplot " + scheduler_2_name + " produced (extra) context switch / JOB")
    ax1.boxplot(algorithm_2_cs_ratio)

    ax1.set_xticklabels([i[1] for i in tests_base_names])

    plt.show()

    # M
    fig1, ax1 = plt.subplots()
    ax1.set_title("Boxplot " + scheduler_1_name + " produced (extra) migrations / JOB")
    ax1.boxplot(algorithm_1_m_ratio)

    ax1.set_xticklabels([i[1] for i in tests_base_names])

    plt.show()

    fig1, ax1 = plt.subplots()
    ax1.set_title("Boxplot " + scheduler_2_name + " produced (extra) migrations / JOB")
    ax1.boxplot(algorithm_2_m_ratio)

    ax1.set_xticklabels([i[1] for i in tests_base_names])

    plt.show()

    # sns.set_theme(style="ticks", palette="pastel")
    #
    # # Load the example tips dataset
    # tips = sns.load_dataset("tips")
    #
    # # Draw a nested boxplot to show bills by day and time
    # sns.boxplot(x="day", y="total_bill",
    #             hue=["smoker", "sex"], palette=["m", "g"],
    #             data=tips)
    # sns.despine(offset=10, trim=True)
    #
    # plt.show()


if __name__ == '__main__':
    do_plots()
