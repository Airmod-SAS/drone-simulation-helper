#!/usr/bin/env python3
"""Example of a mission with a single drone"""

import asyncio
import math
from dataclasses import dataclass
from mavsdk import System
from mavsdk.telemetry import Position, EulerAngle

@dataclass
class Target:
    """Target position"""
    lat: float
    lon: float
    alt: float
    roll: float
    pitch: float
    yaw: float

    def __repr__(self):
        return f"L:{self.lat:.5f}°, l:{self.lon:.5f}°, att:{self.alt:6.2f} m," \
               f"roll:{self.roll:7.2f}°, pitch:{self.pitch:7.2f}°, yaw:{self.yaw:7.2f}°"

def position_to_target(position:Position, angles:EulerAngle|None) -> Target:
    """Convert a position and angles to a Target object"""
    return Target(position.latitude_deg,
                  position.longitude_deg,
                  position.absolute_altitude_m,
                  angles.roll_deg if angles else 0,
                  angles.pitch_deg if angles else 0,
                  angles.yaw_deg if angles else 0)


async def print_position(drone:System):
    """Print the current position of the drone"""
    while True:
        async for position in drone.telemetry.position():
            async for angles in drone.telemetry.attitude_euler():
                target = position_to_target(position, angles)
                print(f"Current position: {target}")
                break
            break
        await asyncio.sleep(1)


async def check_destination(drone:System, target:Target,
                            tolerance:float=0.0001, max_loops:int=20) -> bool:
    """Check if the drone has reached the target position"""
    loop = 0
    while True:
        async for position in drone.telemetry.position():
            current_lat = position.latitude_deg
            current_lon = position.longitude_deg
            current_alt = position.absolute_altitude_m
            break
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

async def goto_destination(drone:System, target:Target,
                           tolerance:float=0.0001, max_loops:int=20) -> bool:
    """Go to destination, and wait until the drone reaches the target position"""
    print(f" Target position: {target}")
    await drone.action.goto_location(target.lat, target.lon, target.alt, target.yaw)
    result = await check_destination(drone, target, tolerance, max_loops)
    print(f" Target position: {target}")
    return result

async def goto_launch(drone:System,lunch:Target):
    """Return to the launch position"""
    async for position in drone.telemetry.home():
        home = position_to_target(position,None)
        break
    print(f"Home    position: {home}")
    print(f"Launch  position: {lunch}")
    await drone.action.return_to_launch()
    result = await check_destination(drone, lunch, max_loops=50)
    print(f"Launch  position: {lunch}")
    return result

async def set_target(drone:System, target_lat:float, target_lon:float,
                     target_alt:float=0, target_yaw:float=0) -> Target:
    """Define a target position relative to the current position of the drone"""
    current_lat = 0
    current_lon = 0
    current_alt = 0

    async for position in drone.telemetry.position():
        current_lat = position.latitude_deg
        current_lon = position.longitude_deg
        current_alt = position.absolute_altitude_m
        break
    return Target(current_lat+target_lat, current_lon+target_lon,
                  current_alt+target_alt, 0,0, target_yaw)

async def run_mission():
    """Run the mission"""
    drone = System()
    await drone.connect("udp://:14540")
    lunch    = await set_target(drone,  0,      0,       0)
    target_1 = await set_target(drone,  0.0001, 0.0001, 10, 10)
    target_2 = await set_target(drone, -0.0001, 0.0003,  5, 60)
    triplet = [lunch,target_1,target_2]

    position_task = asyncio.create_task(print_position(drone))

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
    await asyncio.sleep(1)

    print("Going to second waypoint ...")
    target = triplet[2]
    await goto_destination(drone, target)
    await asyncio.sleep(1)

    print("Going to home ...")
    lunch = triplet[0]
    await goto_launch(drone, lunch)

    print("Landing ...")
    await drone.action.land()

    await asyncio.sleep(20)  # Attendre que l'atterrissage soit terminé

    print("Mission complete!")
    position_task.cancel()

if __name__ == "__main__":
    asyncio.run(run_mission())
