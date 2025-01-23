#!/usr/bin/env bash

. ./config.env

function webots_docker () {
    docker build -t webots ./webots-docker
}

function build_ardupilot() {
    cd ${ARDU_PATH}
    source ~/venv_ardupilot/bin/activate
    ./waf
}

function build_px4() {
    cd ${PX4_PATH}
    source ${PX4_VENV_PATH}/bin/activate
    make
}

function build_betaflight() {
    # https://betaflight.com/docs/development/building/Building-in-Ubuntu
    cd ${BETAFLIGHT_PATH}
    make
}

###### MAIN ######

function usage() {
    echo "Usage: $0 {webots-docker, ardupilot, px4}"
    exit 1
}

if [ $# -eq 0 ]; then
  usage
fi

case $1 in
    webots-docker)
        webots_docker
        ;;
    ardupilot)
        build_ardupilot
        ;;
    px4)
        build_px4
        ;;
    betaflight)
        build_betaflight
        ;;
    *)
        echo "Invalid option."
        usage
        ;;
esac
