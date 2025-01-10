#!/usr/bin/env python3
"""Example of a mission with a single drone"""

import asyncio
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

class TargetManager:


    def __init__(self,drone:System):
        self.drone = drone
        self.position_task = asyncio.create_task(self.print_position())
        pass

    def __del__(self):
        self.position_task.cancel()

    @classmethod
    def position_to_target(cls, position:Position, angles:EulerAngle|None) -> Target:
        """Convert a position and angles to a Target object"""
        return Target(position.latitude_deg,
                    position.longitude_deg,
                    position.absolute_altitude_m,
                    angles.roll_deg if angles else 0,
                    angles.pitch_deg if angles else 0,
                    angles.yaw_deg if angles else 0)

    async def print_position(self):
        """Print the current position of the drone"""
        while True:
            async for position in self.drone.telemetry.position():
                async for angles in self.drone.telemetry.attitude_euler():
                    target = self.position_to_target(position, angles)
                    print(f"Current position: {target}")
                    break
                break
            await asyncio.sleep(1)

