# drone-simulation-help

This project objective is to help begineer to setup a basic Drone simulator environement.

OS target is currently Ubuntu 24.04 LTS, as some tools have Ubuntu libs dependency. It's also work on WSL2 :yum:


I have tried both ArduPilot and PX4 SITL, but i'm currently only able to run PX4 one (with Gazebo).

# TL;DR

## install tools

```shell
./prepare.sh gazebo
./prepare.sh px4
./build.sh px4
./prepare.sh qgroundcontrol
```
wait for reboot (manually `wsl --shutdown` for WSL as reboot does not work properly)

## run simulation
on three different prompt
`./run.sh qgroundcontrol`, `./run.sh px4` and `./run.sh example`

# simulator

There is few scripts to help installation :
- `prepare.sh` : download and install dependencies and sources/bin
- `build.sh` : compile (if needed)
- `run.sh` : execute (with demo example)

## ardupilot

- Ardupilot come with sources, so we need to compile them
- Ardupilot works with Webots simulator

```shell
./prepare.sh ardupilot
./build.sh ardupilot
```

then, once you have installed webots
```shell
./run ardupilot
```

## PX4

- PX4 come with sources, so we need to compile them
- PX4 works with Gazebo simulator

```shell
./prepare.sh px4
./build.sh px4
```

then, once you have installed gazebo
```shell
./run px4
```
this lunch a drone on port on port 14540

you can add additional drones in the simulation,
example
- `./run px4 1` for drone on port 14541
- `./run px4 4` for drone on port 14544

## Webots

Webot can be used in docker or in full install.

- webots need ardupilot as prerequisite
- Webots is used by Ukrenian team.

__note__ not working at all...

### how to install and build

#### with Docker

__note__ black screen on old PC
first, install prerequisite (beware, docker will restart the PC)
```shell
./prepare.sh update-docker
```

build the docker image
```shell
./build.sh webots-docker
```

then run the docker image
```shell
./run.sh webots-docker
webots /tmp/ardupilot/libraries/SITL/examples/Webots_Python/worlds/iris.wbt
```

#### without docker

fist, install prerequisite

```shell
./prepare.sh webots
```

then,
```shell
./run.sh webots
```

even if we follow the doc like Ukrenian, i'm not able to takeoff the drone

## Gazebo

- Gazebo is used by PX4

```shell
./prepare.sh gazebo
```

there is no need to run it, PX4 already do it

## QGroundControl

the ground controller that without nothing work...

it's does not care about other tools, it's like it's own life.

```shell
./prepare.sh qgroundcontrol
./run.sh qgroundcontrol
```

# Test

here, some information about tools to run something in the simulation

## Mavlink

there is some mavSDK python in _scripts_ folder

- test.py is a basic auto flight that go to 2 waypoint then back to home.
  - `test.py` alone run one drone (for PX4) basic one on port 14540
  - `test.py 3` will normally connect to the drone on port 14543