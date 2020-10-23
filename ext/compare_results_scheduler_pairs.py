import csv
import json
from typing import List, Tuple

import scipy.stats
import matplotlib.pyplot as plt


def compare_results():
    tests_base_names = ["out/2/8/", "out/2/16/", "out/2/24/", "out/2/32/", "out/2/40/", "out/4/16/", "out/4/32/",
                        "out/4/48/", "out/4/64/", "out/4/80/"]
    scheduler_1_name = "clustered_aiecs"
    scheduler_2_name = "run"

    for tests_base_name in tests_base_names:

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
                                     scheduler_produced_context_switch_number_scheduler_2,
                                     mandatory_context_switch_number,
                                     migrations_number_scheduler_1, migrations_number_scheduler_2))
            except Exception as e:
                print("Has fail", name)
                pass

        print("Test name:", tests_base_name)
        print("Analyzed", number_of_test_analyzed, "of", number_of_tests, "tests")
        print("\t Better", scheduler_1_name)
        print("\t\t In context switch", better_scheduler_1_in_cs)
        print("\t\t In migrations", better_scheduler_1_in_m)

        print("\t Better", scheduler_2_name)
        print("\t\t In context switch", better_scheduler_2_in_cs)
        print("\t\t In migrations", better_scheduler_2_in_m)

        print("\t Equal booth schedulers")
        print("\t\t In context switch", equal_booth_schedulers_in_cs)
        print("\t\t In migrations", equal_booth_schedulers_in_m)


if __name__ == '__main__':
    compare_results()
