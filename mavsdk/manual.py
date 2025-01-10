#!/usr/bin/env python3

# Warning: Only try this in simulation!
#          The direct attitude interface is a low level interface to be used
#          with caution. On real vehicles the thrust values are likely not
#          adjusted properly and you need to close the loop using altitude.

import asyncio
import argparse
from mavsdk import System
from mavsdk.offboard import (Attitude, OffboardError)
from target_log import TargetManager

async def run_mission(drone_id:int):
    """ Does Offboard control using attitude commands. """

    drone = System(mavsdk_server_address="localhost", port=50060+drone_id)
    await drone.connect(system_address="udp://:14540")

    tgm = TargetManager(drone)

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Setting initial setpoint")
    await drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.0))

    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: \
              {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
        return

    print("-- takeoff")
    await drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.8))
    await asyncio.sleep(2)

    print("-- stabilize")
    await drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.715))
    await asyncio.sleep(10)

    for i in range(10):
        print(f"-- go {i}")
        await drone.offboard.set_attitude(Attitude(0.0, -i, 0, 0.72))
        await asyncio.sleep(1)

    print("-- Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
              {error._result.result}")

    await drone.action.land()


if __name__ == "__main__":
    def get_args():
        parser = argparse.ArgumentParser(description="Drone manual script")
        parser.add_argument("-d","--drone_id", type=int, default=0, help="Drone identifier")
        return parser.parse_args()

    args = get_args()
    asyncio.run(run_mission(args.drone_id))
