import csv
import json
from typing import List, Tuple

import scipy.stats
import matplotlib.pyplot as plt


def compare_results():
    tests_base_name = "out/4/16/"
    scheduler_1_name = "run"
    scheduler_2_name = "run_improved"

    better_scheduler_1_in_cs = 0
    better_scheduler_2_in_cs = 0
    equal_booth_schedulers_in_cs = 0

    better_scheduler_1_in_m = 0
    better_scheduler_2_in_m = 0
    equal_booth_schedulers_in_m = 0

    number_of_tests = 200

    number_of_test_analyzed = 0

    # [CS ALG1, CS ALG2, CS MANDATORY, M ALG1, M ALG2]
    grouped_info: List[Tuple[int, int, int, int, int]] = []

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

            # Context switch comparison
            if scheduler_produced_context_switch_number_scheduler_1 < \
                    scheduler_produced_context_switch_number_scheduler_2:
                better_scheduler_1_in_cs += 1
            elif scheduler_produced_context_switch_number_scheduler_2 < \
                    scheduler_produced_context_switch_number_scheduler_1:
                better_scheduler_2_in_cs += 1
            else:
                equal_booth_schedulers_in_cs += 1

            # Migrations comparison
            if migrations_number_scheduler_1 < migrations_number_scheduler_2:
                better_scheduler_1_in_m += 1
            elif migrations_number_scheduler_2 < migrations_number_scheduler_1:
                better_scheduler_2_in_m += 1
            else:
                equal_booth_schedulers_in_m += 1

            number_of_test_analyzed += 1

            grouped_info.append((scheduler_produced_context_switch_number_scheduler_1,
                                 scheduler_produced_context_switch_number_scheduler_2, mandatory_context_switch_number,
                                 migrations_number_scheduler_1, migrations_number_scheduler_2))
        except Exception as e:
            print("Has fail", name)
            pass

    # (Algorithm 2 CS - Algorithm 1 CS) / Mandatory CS
    data_to_obtain_statics_cs_1 = [(CS_ALG2 - CS_ALG1) / CS_MANDATORY for
                                   (CS_ALG1, CS_ALG2, CS_MANDATORY, M_ALG1, M_ALG2)
                                   in grouped_info]

    # (Algorithm 2 CS / Algorithm 1 CS)
    data_to_obtain_statics_cs_2 = [CS_ALG2 / CS_ALG1 for (CS_ALG1, CS_ALG2, CS_MANDATORY, M_ALG1, M_ALG2)
                                   in grouped_info]

    # (Algorithm 2 CS - Algorithm 1 CS)
    data_to_obtain_statics_cs_3 = [CS_ALG2 - CS_ALG1 for (CS_ALG1, CS_ALG2, CS_MANDATORY, M_ALG1, M_ALG2)
                                   in grouped_info]

    # Algorithm 1 CS / Mandatory CS
    data_to_obtain_statics_cs_4 = [CS_ALG1 / CS_MANDATORY for
                                   (CS_ALG1, CS_ALG2, CS_MANDATORY, M_ALG1, M_ALG2)
                                   in grouped_info]

    # Algorithm 2 CS / Mandatory CS
    data_to_obtain_statics_cs_5 = [CS_ALG2 / CS_MANDATORY for
                                   (CS_ALG1, CS_ALG2, CS_MANDATORY, M_ALG1, M_ALG2)
                                   in grouped_info]

    # shapiro_result = scipy.stats.shapiro(data_to_obtain_statics_cs)
    # shapiro_result_2 = scipy.stats.shapiro(data_to_obtain_statics_cs_2)
    # shapiro_result_3 = scipy.stats.shapiro(data_to_obtain_statics_cs_3)
    # shapiro_result_4 = scipy.stats.shapiro(data_to_obtain_statics_cs_4)
    # shapiro_result_5 = scipy.stats.shapiro(data_to_obtain_statics_cs_5)

    # fig1, ax1 = plt.subplots()
    # ax1.set_title(
    #     "Context switch Boxplot " + tests_base_name + " " + "(" + scheduler_2_name + "-"
    #     + scheduler_1_name + ") / Mandatory")
    # ax1.boxplot(data_to_obtain_statics_cs_1)
    # plt.show()
    #
    # fig1, ax1 = plt.subplots()
    # ax1.set_title(
    #     "Context switch Boxplot " + tests_base_name + " " + "(" + scheduler_2_name + "/" + scheduler_1_name + ")")
    # ax1.boxplot(data_to_obtain_statics_cs_2)
    # plt.show()
    #
    # fig1, ax1 = plt.subplots()
    # ax1.set_title(
    #     "Context switch Boxplot " + tests_base_name + " " + "(" + scheduler_2_name + "-" + scheduler_1_name + ")")
    # ax1.boxplot(data_to_obtain_statics_cs_3)
    # plt.show()

    fig1, ax1 = plt.subplots()
    ax1.set_title("Context switch Boxplot " + tests_base_name + " " + "(" + scheduler_1_name + ") / Mandatory")
    ax1.boxplot(data_to_obtain_statics_cs_4)
    plt.show()

    fig1, ax1 = plt.subplots()
    ax1.set_title("Context switch Boxplot " + tests_base_name + " " + "(" + scheduler_2_name + ") / Mandatory")
    ax1.boxplot(data_to_obtain_statics_cs_5)
    plt.show()

    print("Better", scheduler_1_name, "in context switch", better_scheduler_1_in_cs)
    print("Better", scheduler_1_name, "in migrations", better_scheduler_1_in_m)

    print("Better", scheduler_2_name, "in context switch", better_scheduler_2_in_cs)
    print("Better", scheduler_2_name, "in migrations", better_scheduler_2_in_m)

    print("Equal booth schedulers in context switch", equal_booth_schedulers_in_cs)
    print("Equal booth schedulers in context migrations", equal_booth_schedulers_in_m)

    print("Analyzed", number_of_test_analyzed, "of", number_of_tests, "tests")


if __name__ == '__main__':
    compare_results()
