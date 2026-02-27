from machine import Pin
import time

BTN_GPIO = [0, 1, 2, 3, 4, 5, 6, 7]
VISUALISATION_GPIO = 15
VISUALISATION_HOLD_MS = 3000

types = [
    "Normal", "Feu", "Eau", "Plante", "Electrik", "Glace",
    "Combat", "Poison", "Sol", "Vol", "Psy", "Insecte",
    "Roche", "Spectre", "Dragon", "Tenebres", "Acier", "Fee",
]

GPIO_TO_TYPE_BY_STEP = [
    [0, 4, 10],   # GPIO 0: Normal, Electrik, Psy
    [1, 5, 11],   # GPIO 1: Feu, Glace, Insecte
    [2, 6, 12],   # GPIO 2: Eau, Combat, Roche
    [3, 7, 13],   # GPIO 3: Plante, Poison, Spectre
    [8, 14],      # GPIO 4: Sol, Dragon — 2 modes
    [9, 15],      # GPIO 5: Vol, Tenebres — 2 modes
    [16],         # GPIO 6: Acier — 1 mode
    [17],         # GPIO 7: Fee — 1 mode
]

buttons = [Pin(p, Pin.IN, Pin.PULL_UP) for p in BTN_GPIO]
visualisation_button = Pin(VISUALISATION_GPIO, Pin.IN, Pin.PULL_UP)
last = [1] * len(BTN_GPIO)
last_visualisation = 1
visualisation_hold_start = None
visualisation_long_triggered = False


def _step_to_subindex(step, num_modes):
    if num_modes == 1:
        return 0
    if num_modes == 2:
        return 0 if step <= 2 else 1
    return step - 1

def poll(step=1):
    global last, last_visualisation, visualisation_hold_start, visualisation_long_triggered
    type_index = None
    visualisation_pressed = False
    now_ms = time.ticks_ms()

    for i, b in enumerate(buttons):
        v = b.value()
        if last[i] == 1 and v == 0:
            n = len(GPIO_TO_TYPE_BY_STEP[i])
            sub = min(_step_to_subindex(step, n), n - 1)
            type_index = GPIO_TO_TYPE_BY_STEP[i][sub]
        last[i] = v

    vv15 = visualisation_button.value()
    if vv15 == 0:
        if last_visualisation == 1:
            visualisation_hold_start = now_ms
            visualisation_long_triggered = False
        elif visualisation_hold_start is not None and not visualisation_long_triggered:
            if time.ticks_diff(now_ms, visualisation_hold_start) >= VISUALISATION_HOLD_MS:
                visualisation_pressed = True
                visualisation_long_triggered = True
    else:
        visualisation_hold_start = None
        visualisation_long_triggered = False
    last_visualisation = vv15

    return type_index, visualisation_pressed


def poll_buttons(step=1):
    type_index, visualisation_pressed = poll(step)
    if visualisation_pressed:
        return 18
    return type_index
