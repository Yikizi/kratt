#!/usr/bin/env python3
"""
Test script to verify WiZ lamp connection
"""
import asyncio
from pywizlight import wizlight, PilotBuilder

LAMP_IP = "172.20.10.5"


async def test_lamp():
    """Test connection and color control with WiZ lamp"""
    bulb = wizlight(LAMP_IP)

    print(f"🔍 Testing connection to lamp at {LAMP_IP}...")

    try:
        # Get current state
        state = await bulb.updateState()
        print(f"✅ Connection successful!")
        print(f"   Lamp is: {'ON' if state.get_state() else 'OFF'}")
        print(f"   Brightness: {state.get_brightness()}")
        print(f"   Current RGB: {state.get_rgb()}")

        # Test: Turn on and set to red
        print("\n🔴 Testing RED color...")
        await bulb.turn_on(PilotBuilder(rgb=(255, 0, 0)))
        await asyncio.sleep(2)

        # Test: Set to green
        print("🟢 Testing GREEN color...")
        await bulb.turn_on(PilotBuilder(rgb=(0, 255, 0)))
        await asyncio.sleep(2)

        # Test: Set to blue
        print("🔵 Testing BLUE color...")
        await bulb.turn_on(PilotBuilder(rgb=(0, 0, 255)))
        await asyncio.sleep(2)

        print("\n✅ All tests passed! Lamp is working correctly.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_lamp())
