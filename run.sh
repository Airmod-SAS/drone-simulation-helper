#!/usr/bin/env bash

. ./config.env

DRONE_ID=0

function webots_docker() {
    xhost +local:root > /dev/null 2>&1
    docker run -it -e DISPLAY -v ${ARDU_PATH}:/tmp/ardupilot:ro -v /tmp/.X11-unix:/tmp/.X11-unix:rw webots:latest
}

function ardupilot() {
    cd ${ARDU_PATH}
    # because ardupilot create a venv, in user folder
    ./Tools/autotest/sim_vehicle.py -v ArduCopter -w --model webots-python --add-param=./libraries/SITL/examples/Webots_Python/params/iris.parm
}

function webots() {
    webots ${ARDU_PATH}/libraries/SITL/examples/Webots_Python/worlds/iris.wbt
}

function px4() {
    echo "Starting PX4 simulation for drone ${DRONE_ID}"
    cd ${PX4_PATH}
    source ${PX4_VENV_PATH}/bin/activate
    if [ "${DRONE_ID}" == "0" ]; then
        echo "Starting simulation"
        make px4_sitl gz_x500
    else
        echo "Add copter ${DRONE_ID}"
        X=$((DRONE_ID / 3 * 2))
        Y=$((DRONE_ID % 3 * 2))
        PX4_GZ_STANDALONE=1 PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500 PX4_GZ_MODEL_POSE="$X,$Y" ./build/px4_sitl_default/bin/px4 -i ${DRONE_ID}
    fi
}

function qgroundcontrol() {
    cd ${QGC_PATH}
    ./QGroundControl.AppImage
}

function run_example() {
    echo "Running example for drone ${DRONE_ID}"
    cd ${SCRIPTS_PATH}
    source ${PX4_VENV_PATH}/bin/activate
    ./example.py -d ${DRONE_ID}
}

function mavsdk_server() {
    echo "Running MavSDK server for drone ${DRONE_ID}"
    cd ${SCRIPTS_PATH}
    source ${PX4_VENV_PATH}/bin/activate
    ${PX4_VENV_PATH}/lib/python*/site-packages/mavsdk/bin/mavsdk_server udp://:$((14540 + DRONE_ID)) -p $((50060 + DRONE_ID))
}

###### MAIN ######

function usage() {
    echo "Usage: $0 {webots-docker, ardupilot, webots, px4 <id>, qgroundcontrol, example <id>, mavsdk <id>}"
    exit 1
}

if [ $# -eq 0 ]; then
    usage
fi

if [ $# -eq 2 ]; then
    DRONE_ID=$2
fi

case $1 in
    webots-docker)
        webots_docker
        ;;
    ardupilot)
        ardupilot
        ;;
    webots)
        webots
        ;;
    px4)
        px4
        ;;
    qgroundcontrol)
        qgroundcontrol
        ;;
    example)
        run_example
        ;;
    mavsdk)
        mavsdk_server
        ;;
    *)
        echo "Invalid option."
        usage
        ;;
esac
