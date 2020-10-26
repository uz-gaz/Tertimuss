import json


def check_schedulability():
    tests_base_names = ["out/2/8/", "out/2/16/", "out/2/24/", "out/2/32/", "out/2/40/", "out/4/16/", "out/4/32/",
                        "out/4/48/", "out/4/64/", "out/4/80/"]
    scheduler_name = "clustered_aiecs"

    for tests_base_name in tests_base_names:
        number_of_tests = 200

        number_of_scheduled_tests = 0

        for i in range(number_of_tests):
            name = "test_" + str(i)
            try:
                save_path = tests_base_name
                simulation_name = name + "_"
                with open(save_path + simulation_name + scheduler_name + "_execution_percentage_statics.json",
                          "r") as read_file:
                    decoded_json = json.load(read_file)
                    number_of_missed_deadlines = decoded_json["statics"]["number_of_missed_deadlines"]
                    if number_of_missed_deadlines == 0:
                        number_of_scheduled_tests = number_of_scheduled_tests + 1

            except Exception as e:
                print("Have fail", name)
                pass

        print(tests_base_name, ":", number_of_scheduled_tests, "/", number_of_tests)


if __name__ == '__main__':
    check_schedulability()
