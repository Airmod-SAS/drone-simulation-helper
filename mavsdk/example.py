#!/usr/bin/env python3
"""Example of a mission with a single drone"""

import asyncio
import math
from mavsdk import System
from target_log import Target, TargetManager
import argparse


async def _get_position_info(drone:System) -> tuple:
    current_lat = 0
    current_lon = 0
    current_alt = 0
    async for position in drone.telemetry.position():
        current_lat = position.latitude_deg
        current_lon = position.longitude_deg
        current_alt = position.absolute_altitude_m
        break
    return current_lat, current_lon, current_alt
async def check_destination(drone:System, target:Target,
                            tolerance:float=0.0001, max_loops:int=20) -> bool:
    """Check if the drone has reached the target position"""
    loop = 0
    while True:
        current_lat, current_lon, current_alt = await _get_position_info(drone)
        loop += 1

        # Calculer la distance entre la position actuelle et la cible
        distance = math.sqrt(
            (current_lat - target.lat) ** 2 +
            (current_lon - target.lon) ** 2
        )

        altitude_diff = abs(current_alt - target.alt)

        # Vérifier si le drone est dans la tolérance
        if distance < tolerance and altitude_diff < 1.0:  # 1 mètre de tolérance pour l'altitude
            return True

        if loop > max_loops:
            print("Timeout")
            break

        await asyncio.sleep(1)

    return False

async def set_target(drone:System, target_lat:float, target_lon:float,
                    target_alt:float=0, target_yaw:float=0) -> Target:
    """Define a target position relative to the current position of the drone"""
    current_lat, current_lon, current_alt = await _get_position_info(drone)
    return Target(current_lat+target_lat, current_lon+target_lon,
                current_alt+target_alt, 0,0, target_yaw)


async def goto_destination(drone:System, target:Target,
                           tolerance:float=0.0001, max_loops:int=20) -> bool:
    """Go to destination, and wait until the drone reaches the target position"""
    print(f" Target position: {target}")
    await drone.action.goto_location(target.lat, target.lon, target.alt, target.yaw)
    result = await check_destination(drone,target, tolerance, max_loops)
    print(f" Target position: {target}")
    return result

async def goto_launch(drone:System,lunch:Target):
    """Return to the launch position"""
    async for position in drone.telemetry.home():
        home = TargetManager.position_to_target(position,None)
        break
    print(f"Home    position: {home}")
    print(f"Launch  position: {lunch}")
    await drone.action.return_to_launch()
    result = await check_destination(drone,lunch, max_loops=50)
    print(f"Launch  position: {lunch}")
    return result

async def run_mission(drone_id:int):
    """Run the mission"""
    drone = System(mavsdk_server_address="localhost", port=50060+drone_id)
    await drone.connect()
    tgm = TargetManager(drone)
    lunch    = await set_target(drone,0,      0,       0)
    target_1 = await set_target(drone,0.0001, 0.0001, 10, 10)
    target_2 = await set_target(drone,-0.0001, 0.0003,  5, 60)
    triplet = [lunch,target_1,target_2]

    print(f"{triplet[0]=}")
    print(f"{triplet[1]=}")
    print(f"{triplet[2]=}")

    print("Arming the drone ...")
    await drone.action.arm()

    print("Taking off ...")
    await drone.action.takeoff()
    await asyncio.sleep(10)


    print("Going to first waypoint ...")
    target = triplet[1]
    await goto_destination(drone, target)
    await asyncio.sleep(10)

    print("Going to second waypoint ...")
    target = triplet[2]
    await goto_destination(drone, target)
    await asyncio.sleep(10)

    print("Going to home ...")
    lunch = triplet[0]
    await goto_launch(drone, lunch)

    print("Landing ...")
    await drone.action.land()

    await asyncio.sleep(10)  # Attendre que l'atterrissage soit terminé

    print("Mission complete!")

if __name__ == "__main__":
    def get_args():
        parser = argparse.ArgumentParser(description="Drone mission script")
        parser.add_argument("-d","--drone_id", type=int, default=0, help="Drone identifier")
        return parser.parse_args()

    args = get_args()
    asyncio.run(run_mission(args.drone_id))
