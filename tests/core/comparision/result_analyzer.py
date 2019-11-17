import csv
import json
import unittest


class ResultAnalyzer(unittest.TestCase):
    def test_result_analyzer(self):
        test_path = "out/experimentation/"
        test_to_analyze = [0, 1, 3, 4, 14, 27, 29, 33, 35, 38]

        recap = []
        # 0 -> JDEDS
        # 0, 0 -> context switch
        # 0, 1 -> context switch scheduler
        # 0, 2 -> context switch mandatory
        # 0, 3 -> migrations

        for i in test_to_analyze:
            name = "test_" + str(i)
            simulation_name = name + "_"
            with open(test_path + simulation_name + "jdeds_context_switch_statics.json", "r") as read_file:
                decoded_json_jdeds = json.load(read_file)
            with open(test_path + simulation_name + "run_context_switch_statics.json", "r") as read_file:
                decoded_json_run = json.load(read_file)

            recap.append([
                i,
                decoded_json_jdeds["statics"]["total_context_switch_number"],
                decoded_json_jdeds["statics"]["scheduler_produced_context_switch_number"],
                decoded_json_jdeds["statics"]["mandatory_context_switch_number"],
                decoded_json_jdeds["statics"]["migrations_number"],

                decoded_json_run["statics"]["total_context_switch_number"],
                decoded_json_run["statics"]["scheduler_produced_context_switch_number"],
                decoded_json_run["statics"]["mandatory_context_switch_number"],
                decoded_json_run["statics"]["migrations_number"]
            ])

        # Write results to CSV
        with open('results.csv', 'a') as csvFile:
            writer = csv.writer(csvFile)
            header_row = ["Experiment name",

                          "JDEDS total context switch number", "JDEDS scheduler produced context switch number",
                          "JDEDS mandatory context switch number", "JDEDS  migrations number",

                          "RUN total context switch number", "RUN scheduler produced context switch number",
                          "RUN mandatory context switch number", "RUN  migrations number"
                          ]

            writer.writerow(header_row)

            for row in recap:
                writer.writerow(row)
        csvFile.close()


if __name__ == '__main__':
    unittest.main()
