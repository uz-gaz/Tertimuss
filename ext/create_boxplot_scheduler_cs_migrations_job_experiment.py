import json
from typing import List, Tuple

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
    scheduler_name = "clustered_aiecs"

    number_of_tests = 200

    # Plot limits
    plot_limits_cs = (-0.1, 3.5)
    plot_limits_m = (-0.1, 3.5)

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
    algorithm_cs_ratio = [[CS_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local] for
                          grouped_info_local in grouped_info]

    # Algorithm M / JOBS
    algorithm_m_ratio = [[M_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local] for
                         grouped_info_local in grouped_info]

    # CS
    fig1, ax1 = plt.subplots()
    ax1.set_ylim(plot_limits_cs)
    ax1.set_title("Boxplot " + scheduler_name + " produced (extra) \n (context switch experiment) / (JOBS experiment)")
    ax1.boxplot(algorithm_cs_ratio)

    ax1.set_xticklabels([i[1] for i in tests_base_names])

    #plt.show()
    fig1.savefig('out/plots/' + scheduler_name + '_boxplot_context_switch_job_experiment.png', bbox_inches='tight')

    # M
    fig1, ax1 = plt.subplots()
    ax1.set_ylim(plot_limits_m)
    ax1.set_title("Boxplot " + scheduler_name + " produced (extra) \n (context switch experiment) / (JOBS experiment)")
    ax1.boxplot(algorithm_m_ratio)

    ax1.set_xticklabels([i[1] for i in tests_base_names])

    #plt.show()
    fig1.savefig('out/plots/' + scheduler_name + '_boxplot_migrations_job_experiment.png', bbox_inches='tight')


if __name__ == '__main__':
    do_plots()
