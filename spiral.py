"""The goal of this sketch is to determine how many LED are left in the cut segment. Also it could be used as an animation in the final product."""

import board
import neopixel
import time

# Which pin the data line of the NeoPixel strip is connected to
NEOPIXEL_PIN = board.A1
# How many LED are tucked in the back of the twintail holder, not visible
LEDS_TO_SKIP = 3
# How many LEDs are actually part of the accessory
LEDS_IN_LOOP = 125
# Controls the speed of the animation, how many LEDs to light up/turn off per second.
LEDS_PER_SECOND = 100
BRIGHTNESS = 0.8
RED = (255, 0, 0)
BLACK = (0, 0, 0)

pixels = neopixel.NeoPixel(NEOPIXEL_PIN, LEDS_TO_SKIP + LEDS_IN_LOOP, brightness=BRIGHTNESS)

color = RED
while True:
    for i in range(LEDS_TO_SKIP, LEDS_TO_SKIP + LEDS_IN_LOOP):
        pixels[i] = color
        time.sleep(1/LEDS_PER_SECOND)
    if color == RED:
        color = BLACK
    else:
        color = RED
