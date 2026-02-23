from machine import Pin

# Pins physiques 4, 5, 6, 7
led1 = Pin(2, Pin.OUT)
led2 = Pin(3, Pin.OUT)
led3 = Pin(4, Pin.OUT)
led4 = Pin(5, Pin.OUT)

leds = [led1, led2, led3, led4]


def set_led(index, on):
    """Allume (True) ou éteint (False) la LED à l'index 0-3."""
    if 0 <= index < len(leds):
        leds[index].value(1 if on else 0)


def all_off():
    """Éteint toutes les LEDs."""
    for led in leds:
        led.off()


def all_on():
    """Allume toutes les LEDs."""
    for led in leds:
        led.on()

