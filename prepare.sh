#!/usr/bin/env bash

source ./config.env

function update_docker() {
    echo "Docker will be reinstalled and the system will reboot. Do you want to continue? (Y/n)"
    read -r response
    if [[ "$response" != "Y" && "$response" != "y" ]]; then
        echo "Operation cancelled."
        exit 1
    fi

    #remove previous installations (potentially unofficial)
    for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
        sudo apt-get remove $pkg;
    done
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" ,  \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

    # install latest official docker
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    echo "Everything is ready. system will reboot in 5 secs."
    sleep 5
    # reboot to apply changes
    reboot
}

function install_webots() {
    sudo apt-add-repository -y --remove 'deb https://cyberbotics.com/debian/ binary-amd64/'
    sudo mkdir -p /etc/apt/keyrings
    cd /etc/apt/keyrings
    sudo wget -q https://cyberbotics.com/Cyberbotics.asc
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/Cyberbotics.asc] https://cyberbotics.com/debian binary-amd64/" ,  sudo tee /etc/apt/sources.list.d/Cyberbotics.list
    sudo apt update
    sudo apt install webots
}

function download_ardupilot() {
    # download ardupilot
    if [ -d "ardupilot" ]; then
        echo "Ardupilot already exists. Do you want to update it? (Y/n)"
        read -r response
        if [[ "$response" != "Y" && "$response" != "y" ]]; then
            echo "Operation cancelled."
            exit 1
        fi
        cd ardupilot
        git restore .
        git pull
    else
        git clone https://github.com/ArduPilot/ardupilot.git
    fi
}

function download_px4() {
    . ${PX4_VENV_PATH}/bin/activate
    # download px4
    if [ -d "PX4-Autopilot" ]; then
        echo "PX4-Autopilot already exists. Do you want to update it? (Y/n)"
        read -r response
        if [[ "$response" != "Y" && "$response" != "y" ]]; then
            echo "Operation cancelled."
            exit 1
        fi
        cd PX4-Autopilot
        git restore .
        git pull
    else
        git clone https://github.com/PX4/PX4-Autopilot.git
    fi
    ${PX4_PATH}/Tools/setup/ubuntu.sh
}

function download_gz {
    sudo apt-get update
    sudo apt-get install curl lsb-release gnupg
    sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
    sudo apt-get update
    sudo apt-get install gz-harmonic
}

function download_qgroundcontrol() {
    echo "QGroundControl will be installed and the system will reboot. Do you want to continue? (Y/n)"
    read -r response
    if [[ "$response" != "Y" && "$response" != "y" ]]; then
        echo "Operation cancelled."
        exit 1
    fi
    sudo usermod -a -G dialout $USER
    sudo apt-get remove modemmanager -y
    sudo apt install gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl -y
    sudo apt install libfuse2 libpulse-dev -y
    sudo apt install libxcb-xinerama0 libxkbcommon-x11-0 libxcb-cursor-dev -y
    mkdir QGroundControl
    wget https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl.AppImage -O ${QGC_PATH}/QGroundControl.AppImage
    chmod +x ${QGC_PATH}/QGroundControl.AppImage
    echo "Everything is ready. system will reboot in 5 secs."
    sleep 5
    # reboot to apply changes
    reboot
}

function scripts_venv() {
    sudo apt-get install python3-venv
    python3 -m venv ${PX4_VENV_PATH}
    source ${PX4_VENV_PATH}/bin/activate
    pip install -U pip
    pip install mavsdk
}

function download_ros2_and_dependencies() {
    # support UTF-8
    sudo apt update && sudo apt install locales
    sudo locale-gen en_US en_US.UTF-8
    sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
    export LANG=en_US.UTF-8

    # setup sources repository
    sudo apt install software-properties-common
    sudo add-apt-repository universe

    # setup keys
    sudo apt update && sudo apt install curl -y
    sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

    # add repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

    # install dependencies
    sudo apt update && sudo apt install -y \
    python3-flake8-blind-except \
    python3-flake8-class-newline \
    python3-flake8-deprecated \
    python3-mypy \
    python3-pip \
    python3-pytest \
    python3-pytest-cov \
    python3-pytest-mock \
    python3-pytest-repeat \
    python3-pytest-rerunfailures \
    python3-pytest-runner \
    python3-pytest-timeout \
    ros-dev-tools

    # get ROS2 code
    mkdir -p ${ROS2_PATH}/src
    cd ${ROS2_PATH}
    vcs import --input https://raw.githubusercontent.com/ros2/ros2/jazzy/ros2.repos src

    # add missing dependencies
    sudo apt upgrade
    sudo rosdep init
    rosdep update
    rosdep install --from-paths src --ignore-src -y --skip-keys "fastcdr rti-connext-dds-6.0.1 urdfdom_headers"

    # update bashrc
    if ! grep -Fxq "# source ROS2" ~/.bashrc; then
        echo "# source ROS2" >> ~/.bashrc
        echo ". ${ROS2_PATH}/install/local_setup.bash" >> ~/.bashrc
    fi
}

###### MAIN ######

function usage() {
    echo "Usage: $0 {update-docker, ardupilot, webots, px4, gazebo, qgroundcontrol, venv, ros2}"
    exit 1
}

if [ $# -eq 0 ]; then
    usage
fi

case $1 in
    update-docker)
        update_docker
        ;;
    ardupilot)
        download_ardupilot
        ;;
    webots)
        install_webots
        ;;
    px4)
        scripts_venv
        download_px4
        ;;
    gazebo)
        download_gz
        ;;
    qgroundcontrol)
        download_qgroundcontrol
        ;;
    venv)
        scripts_venv
        ;;
    ros2)
        download_ros2_and_dependencies
        ;;
    *)
        echo "Invalid option."
        usage
        ;;
esac
