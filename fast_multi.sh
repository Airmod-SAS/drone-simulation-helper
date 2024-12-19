#!/usr/bin/env bash

drone_count=$(($1 - 1))

if [ $drone_count -ge 9 ]; then
    echo "Max 9 drones supported"
    exit 1
fi

gnome-terminal --title="GroundController"  -- /bin/bash ./run.sh qgroundcontrol
sleep 2
gnome-terminal --title="PX4 Drone 0" -- /bin/bash ./run.sh px4 0
sleep 10
for ((i=1; i<=drone_count; i++)); do
    gnome-terminal --title="PX4 Drone $i" -- /bin/bash ./run.sh px4 $i
done
sleep 10
for ((i=0; i<=drone_count; i++)); do
    gnome-terminal --title="MavSDK server $i" -- /bin/bash ./run.sh mavsdk $i
done

