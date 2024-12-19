gnome-terminal --title="GroundController"  -- /bin/bash ./run.sh qgroundcontrol
sleep 1
gnome-terminal --title="PX4 Drone 0" -- /bin/bash ./run.sh px4 0
sleep 2
gnome-terminal --title="MavSDK server 0"-- /bin/bash ./run.sh mavsdk 0
sleep 3
gnome-terminal --title="Example 0" -- /bin/bash ./run.sh example 0
