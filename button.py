from machine import Pin

btn_pins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 21, 22]
types = [
    "Normal", "Feu", "Eau", "Plante", "Electrik", "Glace",
    "Combat", "Poison", "Sol", "Vol", "Psy", "Insecte",
    "Roche", "Spectre", "Dragon", "Tenebres", "Acier", "Fee"
]

buttons = [Pin(p, Pin.IN, Pin.PULL_UP) for p in btn_pins]
last = [1] * len(buttons)


def poll():
    """Retourne l'index du bouton appuyé (front descendant), ou None."""
    pressed = None
    for i, b in enumerate(buttons):
        v = b.value()
        if last[i] == 1 and v == 0:
            pressed = i
        last[i] = v
    return pressed

