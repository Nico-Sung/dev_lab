from machine import Pin
import neopixel
import time

NUM_LEDS = 1

pin = Pin(27)

np = neopixel.NeoPixel(pin, NUM_LEDS)

while True:
    np[0] = (255, 0, 0)   # rouge
    np.write()
    time.sleep(1)

    np[0] = (0, 255, 0)   # vert
    np.write()
    time.sleep(1)

    np[0] = (0, 0, 255)   # bleu
    np.write()
    time.sleep(1)

    np[0] = (0, 0, 0)     # éteint
    np.write()
    time.sleep(1)

