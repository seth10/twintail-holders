"""
This sketch uses the free Adafruit Bluefruit LE Connect App. Download and open the app, check the "Must have UART Service" filter, and tap the "Connect" button next to the one device named something like "CIRCUITPYc11325".
Then navigate to Controller > Control Pad, and use buttons 1-4 to control the brightness. 0: 0% (off), 1: 30%, 2: 70%, 3: 100%.
"""

import asyncio
import board
import neopixel

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.button_packet import ButtonPacket

# Display constants
INITIAL_BRIGHTNESS = 0.8
RED = (255, 0, 0)
BLACK = (0, 0, 0)

class NeoPixelConfig:
    # Which pins the data lines of the NeoPixel strips are each connected to
    data_pin: Pin
    # How many LED are tucked in the back of the twintail holder, not visible
    leds_to_skip: int
    # How many LEDs are actually part of the accessory
    leds_in_loop: int
    
    def __init__(self, data_pin, leds_to_skip, leds_in_loop):
        self.data_pin = data_pin
        self.leds_to_skip = leds_to_skip
        self.leds_in_loop = leds_in_loop

# index 8 is the first LED I want to light up, 153 is the last one that exists, the usable loop is 146 long
left_cfg = NeoPixelConfig(data_pin=board.A0, leds_to_skip=7, leds_in_loop=146)
# index 4 is the first LED I want to light up, 149 is the last one that exists, the usable loop is 146 long
right_cfg = NeoPixelConfig(data_pin=board.A1, leds_to_skip=3, leds_in_loop=146)
left = neopixel.NeoPixel(left_cfg.data_pin, left_cfg.leds_to_skip + 1 + left_cfg.leds_in_loop, brightness=INITIAL_BRIGHTNESS, auto_write=False)
right = neopixel.NeoPixel(right_cfg.data_pin, right_cfg.leds_to_skip + 1 + right_cfg.leds_in_loop, brightness=INITIAL_BRIGHTNESS, auto_write=False)

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

class Controls:
    def __init__(self):
        self.color = RED
        self.brightness = INITIAL_BRIGHTNESS

async def animate_neopixels(controls):
    while True:
        for i in range(0, left_cfg.leds_in_loop):
            left[left_cfg.leds_to_skip + 1 + i] = controls.color
        for i in range(0, right_cfg.leds_in_loop):
            right[right_cfg.leds_to_skip + 1 + i] = controls.color
        left.brightness = controls.brightness
        right.brightness = controls.brightness
        left.show()
        right.show()
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
                            controls.brightness = 0.0
                        elif packet.button == ButtonPacket.BUTTON_2:
                            controls.brightness = 0.3
                        elif packet.button == ButtonPacket.BUTTON_3:
                            controls.brightness = 0.7
                        elif packet.button == ButtonPacket.BUTTON_4:
                            controls.brightness = 1.0
            await asyncio.sleep(0)

        # If we got here, we lost the connection. Go up to the top of this function and start advertising again, waiting for a connection.

async def main():
    controls = Controls()

    ble_task = asyncio.create_task(monitor_ble_control_pad(controls))
    neopixel_task = asyncio.create_task(animate_neopixels(controls))
    
    # This will run forever, because no tasks ever finish.
    await asyncio.gather(ble_task, neopixel_task)

asyncio.run(main())
