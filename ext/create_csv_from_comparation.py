import csv
import json


def create_csv_from_comparision():
    results_to_print = []
    results_to_print.append(["name", "mandatory context switch number",
                             "context switch number aiecs", "migrations number aiecs",
                             "context switch number run", "migrations number run",
                             "context switch number semipartitioned aiecs", "migrations number semipartitioned aiecs"
                             ])
    tests_base_name = "out/4/24/"
    for i in range(500):
        name = "test_" + str(i)
        print(name)
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

            with open(save_path + simulation_name + "semipartitionedaiecs_context_switch_statics.json",
                      "r") as read_file:
                decoded_json = json.load(read_file)
                total_context_switch_number_semipartitionedaiecs = decoded_json["statics"][
                    "total_context_switch_number"]
                scheduler_produced_context_switch_number_semipartitionedaiecs = decoded_json["statics"][
                    "scheduler_produced_context_switch_number"]
                mandatory_context_switch_number_semipartitionedaiecs = decoded_json["statics"][
                    "mandatory_context_switch_number"]
                migrations_number_semipartitionedaiecs = decoded_json["statics"]["migrations_number"]

            results_to_print.append([name, mandatory_context_switch_number_aiecs,
                                     total_context_switch_number_aiecs, migrations_number_aiecs,
                                     total_context_switch_number_run, migrations_number_run,
                                     total_context_switch_number_semipartitionedaiecs,
                                     migrations_number_semipartitionedaiecs
                                     ])
        except Exception as e:
            print("Ha fallado")
            pass

    with open(tests_base_name + 'results.csv', 'w', newline='') as file:
        for j in results_to_print:
            writer = csv.writer(file)
            writer.writerow(j)


if __name__ == '__main__':
    create_csv_from_comparision()
