#!/usr/bin/env python3

from mavsdk import System
from mavsdk.telemetry import Position, EulerAngle
import asyncio
import math
from dataclasses import dataclass

@dataclass
class Target:
    lat: float
    lon: float
    alt: float
    roll: float
    pitch: float
    yaw: float


    def __repr__(self):
        return f"-L:{self.lat:.5f}°, l:{self.lon:.5f}°, att:{self.alt:6.2f} m," \
               f"roll:{self.roll:7.2f}°, pitch:{self.pitch:7.2f}°, yaw:{self.yaw:7.2f}°-"

def position_to_target(position:Position, angles:EulerAngle|None) -> Target:
    return Target(position.latitude_deg,
                  position.longitude_deg,
                  position.absolute_altitude_m,
                  angles.roll_deg if angles else 0,
                  angles.pitch_deg if angles else 0,
                  angles.yaw_deg if angles else 0)


async def print_position(drone:System):
    while True:
        async for position in drone.telemetry.position():
            async for angles in drone.telemetry.attitude_euler():
                target = position_to_target(position, angles)
                print(f"Current position: --{drone.info.name}-- {target}")
                break
            break
        await asyncio.sleep(1)


async def check_destination(drone:System, target:Target, tolerance:float=0.0001, max_loops:int=20) -> bool:
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

async def goto_destination(drone:System, target:Target, tolerance:float=0.0001, max_loops:int=20) -> bool:
    print(f" Target position: {target}")
    await drone.action.goto_location(target.lat, target.lon, target.alt, target.yaw)
    result = await check_destination(drone, target, tolerance, max_loops)
    print(f" Target position: {target}")
    return result

async def goto_launch(drone:System,lunch:Target):
    async for position in drone.telemetry.home():
        home = position_to_target(position,None)
        break
    print(f"Home    position: {home}")
    print(f"Launch  position: {lunch}")
    await drone.action.return_to_launch()
    result = await check_destination(drone, lunch, max_loops=50)
    print(f"Launch  position: {lunch}")
    return result

async def set_target(drone:System, target_lat:float, target_lon:float, target_alt:float=0, target_yaw:float=0) -> Target:

    current_lat = 0
    current_lon = 0
    current_alt = 0

    async for position in drone.telemetry.position():
        current_lat = position.latitude_deg
        current_lon = position.longitude_deg
        current_alt = position.absolute_altitude_m
        break
    return Target(current_lat+target_lat, current_lon+target_lon, current_alt+target_alt, 0,0, target_yaw)

async def move_forward(drone: System):
    while True:
        await drone.manual_control.set_manual_control_input(1, 1, 1, 10)  # do the mario
        await asyncio.sleep(0.1)

async def run(drone_address_list: list):

    drone = System()

    position_triplet_map = {}
    for drone_address in drone_address_list:
        await drone.connect(drone_address)
        lunch    = await set_target(drone,  0,      0,       0)
        target_1 = await set_target(drone,  0.0001, 0.0001, 10, 10)
        target_2 = await set_target(drone, -0.0001, 0.0003,  5, 60)
        triplet = [lunch,target_1,target_2]

        print(f"{triplet[0]=}")
        print(f"{triplet[1]=}")
        print(f"{triplet[2]=}")
        print(f"{drone_address}")
        position_triplet_map[drone_address]=triplet

    print(f"{position_triplet_map=}")

    for drone_address in drone_address_list:
        print(f"Arming the drone {drone_address}...")
        await drone.connect(drone_address)
        await drone.action.arm()

    for drone_address in drone_address_list:
        print(f"Taking off {drone_address}...")
        await drone.connect(drone_address)
        await drone.action.takeoff()
        await asyncio.sleep(10)


    for drone_address in drone_address_list:
        print(f"Going to first waypoint {drone_address}...")
        await drone.connect(drone_address)
        target = position_triplet_map[drone_address][1]
        print(f"{target=}")
        await drone.action.goto_location(target.lat, target.lon, target.alt, target.yaw)
        await asyncio.sleep(1)

    for drone_address in drone_address_list:
        await drone.connect(drone_address)
        target = position_triplet_map[drone_address][1]
        await check_destination(drone, target)
        print(f" Target position {drone_address}: {target}")

    for drone_address in drone_address_list:
        print(f"Going to second waypoint {drone_address}...")
        await drone.connect(drone_address)
        target = position_triplet_map[drone_address][2]
        await drone.action.goto_location(target.lat, target.lon, target.alt, target.yaw)

    for drone_address in drone_address_list:
        await drone.connect(drone_address)
        target = position_triplet_map[drone_address][2]
        await check_destination(drone, target)
        print(f" Target position {drone_address}: {target}")


    for drone_address in drone_address_list:
        print(f"Going to home {drone_address}...")
        await drone.connect(drone_address)
        lunch = position_triplet_map[drone_address][0]
        await goto_launch(drone, lunch)

    for drone_address in drone_address_list:
        print(f"Landing {drone_address}...")
        await drone.connect(drone_address)
        await drone.action.land()

    await asyncio.sleep(20)  # Attendre que l'atterrissage soit terminé

    print("Mission complete!")

async def drone_driver(id_list:list):

    drone_address_list = []
    for id in id_list:
        drone_address_list.append(f"udp://:1454{id}")
    await run(drone_address_list)



if __name__ == "__main__":
    asyncio.run(drone_driver([0,1]))
