#!/usr/bin/env python3
import asyncio
from multi_drone import drone_driver

if __name__ == "__main__":
    asyncio.run(drone_driver([0]))
