#!/usr/bin/env bash

drone_count=$(($1 - 1))

if [ $drone_count -ge 9 ]; then
    echo "Max 9 drones supported"
    exit 1
fi

for ((i=0; i<=drone_count; i++)); do
    gnome-terminal --title="Python $i mission" -- /bin/bash ./run.sh example $i
done
