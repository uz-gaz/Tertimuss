#!/usr/bin/env bash

python_cli_launcher="../../cli_launcher.py"

actual_iteration=0
total_iteration_number=$(ls -1q | wc -l)

for file in ./specification/* ; do
    echo "${actual_iteration}/${total_iteration_number}"
    python ${python_cli_launcher} -f ${file}
    actual_iteration=$(($actual_iteration + 1))
done
