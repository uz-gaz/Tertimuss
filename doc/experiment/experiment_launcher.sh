#!/usr/bin/env bash

if [[ $# -ne 1 ]]; then
    echo "Bad number of parameters"
    echo "Usage: script_name experiment_name"
    exit 2
fi

python_cli_launcher="../../cli_launcher.py"

actual_iteration=0
total_iteration_number=$(ls -1q | wc -l)

for file in ./specification/${1}/* ; do
    echo "${actual_iteration}/${total_iteration_number}"
    echo "Experiment: ${file}"
    python ${python_cli_launcher} -f ${file}
    actual_iteration=$(($actual_iteration + 1))
done
