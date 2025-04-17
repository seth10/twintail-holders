"""
This sketch uses the free Adafruit Bluefruit LE Connect App. Download and open the app, check the "Must have UART Service" filter, and tap the "Connect" button next to the one device named something like "CIRCUITPYc11325".
Then navigate to Controller > Control Pad, and tap 1 to turn on the lights on both twintail holders, and 2 to turn the lights off.
"""

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.button_packet import ButtonPacket

import asyncio
import board
import neopixel

# Which pins the data lines of the NeoPixel strips are each connected to
NEOPIXEL_PIN1 = board.A0
NEOPIXEL_PIN2 = board.A1
# How many LED are tucked in the back of the twintail holder, not visible
LEDS_TO_SKIP = 0
# How many LEDs are actually part of the accessory
LEDS_IN_LOOP = 156
# Display constants
BRIGHTNESS = 0.8
RED = (255, 0, 0)
BLACK = (0, 0, 0)

pixels1 = neopixel.NeoPixel(NEOPIXEL_PIN1, LEDS_TO_SKIP + LEDS_IN_LOOP, brightness=BRIGHTNESS)
pixels2 = neopixel.NeoPixel(NEOPIXEL_PIN2, LEDS_TO_SKIP + LEDS_IN_LOOP, brightness=BRIGHTNESS)

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

class Controls:
    def __init__(self):
        self.color = RED

async def animate_neopixels(controls):
    while True:
        pixels1.fill(controls.color)
        pixels2.fill(controls.color)
        await asyncio.sleep(0.1)

async def monitor_ble_control_pad(controls):
    while True:
        ble.start_advertising(advertisement)
        while not ble.connected:
            await asyncio.sleep(0)

        while ble.connected:
            if uart.in_waiting:
                packet = Packet.from_stream(uart)
                if isinstance(packet, ButtonPacket):
                    if packet.pressed:
                        if packet.button == ButtonPacket.BUTTON_1:
                            controls.color = RED
                        elif packet.button == ButtonPacket.BUTTON_2:
                            controls.color = BLACK
            await asyncio.sleep(0)

        # If we got here, we lost the connection. Go up to the top of this function and start advertising again, waiting for a connection.

async def main():
    controls = Controls()

    ble_task = asyncio.create_task(monitor_ble_control_pad(controls))
    neopixel_task = asyncio.create_task(animate_neopixels(controls))
    
    # This will run forever, because no tasks ever finish.
    await asyncio.gather(ble_task, neopixel_task)

asyncio.run(main())
