import csv
import json


def compare_results():
    tests_base_name = "run_aiecs_comparation_results/2/16/"

    better_run_in_cs = 0
    better_aiecs_in_cs = 0

    better_run_in_m = 0
    better_aiecs_in_m = 0

    number_of_tests = 200

    number_of_test_analyzed = 0

    for i in range(number_of_tests):
        name = "test_" + str(i)
        try:
            save_path = tests_base_name
            simulation_name = name + "_"
            with open(save_path + simulation_name + "run_context_switch_statics.json", "r") as read_file:
                decoded_json = json.load(read_file)
                total_context_switch_number_run = decoded_json["statics"]["total_context_switch_number"]
                scheduler_produced_context_switch_number_run = decoded_json["statics"][
                    "scheduler_produced_context_switch_number"]
                mandatory_context_switch_number_run = decoded_json["statics"]["mandatory_context_switch_number"]
                migrations_number_run = decoded_json["statics"]["migrations_number"]

            with open(save_path + simulation_name + "aiecs_context_switch_statics.json", "r") as read_file:
                decoded_json = json.load(read_file)
                total_context_switch_number_aiecs = decoded_json["statics"]["total_context_switch_number"]
                scheduler_produced_context_switch_number_aiecs = decoded_json["statics"][
                    "scheduler_produced_context_switch_number"]
                mandatory_context_switch_number_aiecs = decoded_json["statics"]["mandatory_context_switch_number"]
                migrations_number_aiecs = decoded_json["statics"]["migrations_number"]

            # with open(save_path + simulation_name + "semipartitionedaiecs_context_switch_statics.json",
            #           "r") as read_file:
            #     decoded_json = json.load(read_file)
            #     total_context_switch_number_semipartitionedaiecs = decoded_json["statics"][
            #         "total_context_switch_number"]
            #     scheduler_produced_context_switch_number_semipartitionedaiecs = decoded_json["statics"][
            #         "scheduler_produced_context_switch_number"]
            #     mandatory_context_switch_number_semipartitionedaiecs = decoded_json["statics"][
            #         "mandatory_context_switch_number"]
            #     migrations_number_semipartitionedaiecs = decoded_json["statics"]["migrations_number"]

            # Context switch comparison
            if scheduler_produced_context_switch_number_aiecs < scheduler_produced_context_switch_number_run:
                better_aiecs_in_cs += 1
            elif scheduler_produced_context_switch_number_run < scheduler_produced_context_switch_number_aiecs:
                better_run_in_cs += 1
            else:
                better_aiecs_in_cs += 1
                better_run_in_cs += 1

            # Migrations comparison
            if migrations_number_aiecs < migrations_number_run:
                better_aiecs_in_m += 1
            elif migrations_number_run < migrations_number_aiecs:
                better_run_in_m += 1
            else:
                better_aiecs_in_m += 1
                better_run_in_m += 1

            number_of_test_analyzed += 1
        except Exception as e:
            print("Ha fallado")
            pass

    print("Better run in context switch", better_run_in_cs)
    print("Better run in migrations", better_run_in_m)

    print("Better aiecs in context switch", better_aiecs_in_cs)
    print("Better aiecs in migrations", better_aiecs_in_m)

    print("Analyzed", number_of_test_analyzed, "of", number_of_tests, "tests")


if __name__ == '__main__':
    compare_results()
