#!/bin/bash

# Arguments
# 1 -> PID OF PROCESS TO MONITOR
# 2 -> Output file
# 3 -> Time to sleep

while [[ true ]]
do
   ps v $1 | tail -1 >> $2
   sleep $3
done
