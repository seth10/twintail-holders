"""
This sketch requires these libraries:
- adafruit_ble
- adafruit_bluefruit_connect
- asyncio
- neopixel.mpy
Copy these from the lib folder of the bundle (for Version 9.x) zip obtained via https://circuitpython.org/libraries#:~:text=Bundle%20for%20Version%209.x

This project uses the free Adafruit Bluefruit LE Connect App. Download and open the app, check the "Must have UART Service" filter, and tap the "Connect" button next to the one device named something like "CIRCUITPYc11325".
Then navigate to Controller > Control Pad. Tap up or down to increase or decrease the brightness by 20% (it starts at 80%). Press 1 for red, 2 for green, 3 for blue, and 4 for teal (matches the wig).
You can also go to Controller > Color Picker and send a custom color.
When you Ctrl+S to save the sketch and reload the board, you'll need to back out two levels to the screen that says "Modules", before going into Controller > Control Pad again. You _don't_ need to Disconnect and re-Connect.
"""

import asyncio
import board
import neopixel

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.button_packet import ButtonPacket
from adafruit_bluefruit_connect.color_packet import ColorPacket

class Animation:
    # The entire loop is one solid color.
    SOLID = 1
    # Half of the loop is on, this portion moves around the loop.
    REVOLVE = 2
    # LEDs individually turn on around the loop until it's entirely lit up, then similarly turn off one-by-one.
    WIPE = 3
    # All LEDs are on, but the colors fade around in a looping rainbow pattern.
    RAINBOW = 4

# Color constants
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
TEAL = (0, 255, 126)
BLACK = (0, 0, 0)

# Display constants
INITIAL_ANIMATION = Animation.REVOLVE
INITIAL_COLOR = BLUE
INITIAL_BRIGHTNESS = 0.8
BRIGHTNESS_INCREMENT = 0.2

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
        self.animation = INITIAL_ANIMATION
        self.color = INITIAL_COLOR
        self.brightness = INITIAL_BRIGHTNESS
        self.counter = 0

async def animate_neopixels(controls):
    while True:
        left.brightness = controls.brightness
        right.brightness = controls.brightness
        if controls.animation == Animation.SOLID:
            animate_solid(controls, left, left_cfg)
            animate_solid(controls, right, right_cfg)
        elif controls.animation == Animation.REVOLVE:
            animate_revolve(controls, left, left_cfg)
            animate_revolve(controls, right, right_cfg)
        controls.counter += 1
        await asyncio.sleep(0.1)

def animate_solid(controls, leds, cfg):
    leds[cfg.leds_to_skip + 1 : cfg.leds_to_skip + 1 + cfg.leds_in_loop ] = [controls.color] * cfg.leds_in_loop
    leds.show()

def animate_revolve(controls, leds, cfg):
    start = cfg.leds_to_skip + 1
    loop_len = cfg.leds_in_loop
    half = loop_len // 2
    pos = controls.counter % loop_len

    for i in range(loop_len):
        distance = (i - pos) % loop_len
        leds[start + i] = controls.color if distance < half else BLACK

    leds.show()

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
                        if packet.button == ButtonPacket.UP:
                            controls.brightness = min(controls.brightness + BRIGHTNESS_INCREMENT, 1.0)
                        elif packet.button == ButtonPacket.DOWN:
                            controls.brightness = max(controls.brightness - BRIGHTNESS_INCREMENT, 0.0)
                        elif packet.button == ButtonPacket.BUTTON_1:
                            controls.color = RED
                        elif packet.button == ButtonPacket.BUTTON_2:
                            controls.color = GREEN
                        elif packet.button == ButtonPacket.BUTTON_3:
                            controls.color = BLUE
                        elif packet.button == ButtonPacket.BUTTON_4:
                            controls.color = TEAL
                if isinstance(packet, ColorPacket):
                    controls.color = packet.color
            await asyncio.sleep(0)

        # If we got here, we lost the connection. Go up to the top of this function and start advertising again, waiting for a connection.

async def main():
    controls = Controls()

    ble_task = asyncio.create_task(monitor_ble_control_pad(controls))
    neopixel_task = asyncio.create_task(animate_neopixels(controls))
    
    # This will run forever, because no tasks ever finish.
    await asyncio.gather(ble_task, neopixel_task)

asyncio.run(main())
