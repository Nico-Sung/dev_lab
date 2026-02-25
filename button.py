from machine import Pin

BTN_GPIO = [0, 1, 2, 3, 4, 5, 6, 7]
VISUAL_GPIO = 17

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
visual_button = Pin(VISUAL_GPIO, Pin.IN, Pin.PULL_UP)
last = [1] * len(BTN_GPIO)
last_visual = 1


def _step_to_subindex(step, num_modes):
    """Indice dans la liste des types du bouton selon l'étape.
    - 3 modes (GPIO 0-3) : étape 1 -> 0, 2 -> 1, 3 -> 2
    - 2 modes (GPIO 4-5) : étape 1 et 2 -> 0 (Sol/Vol), étape 3 -> 1 (Dragon/Ténèbres)
    - 1 mode (GPIO 6-7) : toujours 0
    """
    if num_modes == 1:
        return 0
    if num_modes == 2:
        return 0 if step <= 2 else 1
    return step - 1

def poll(step=1):
    """
    Poll les 8 boutons physiques + bouton visuel.
    step: 1, 2 ou 3 (étape du mastermind).
    Retourne (type_index, visual_pressed).
    type_index = index dans types (0..17) si un bouton type est appuyé, sinon None.
    visual_pressed = True si le bouton mode visuel (GPIO 17) vient d'être appuyé.
    """
    global last, last_visual
    type_index = None
    visual_pressed = False

    for i, b in enumerate(buttons):
        v = b.value()
        if last[i] == 1 and v == 0:
            n = len(GPIO_TO_TYPE_BY_STEP[i])
            sub = min(_step_to_subindex(step, n), n - 1)
            type_index = GPIO_TO_TYPE_BY_STEP[i][sub]
        last[i] = v

    vv = visual_button.value()
    if last_visual == 1 and vv == 0:
        visual_pressed = True
    last_visual = vv

    return type_index, visual_pressed


def poll_buttons(step=1):
    """
    Retourne l'index de type (0-16) si un bouton type est pressé, 17 si bouton visuel (GPIO 17), sinon None.
    step: 1, 2 ou 3 pour le mapping physique -> type.
    """
    type_index, visual_pressed = poll(step)
    if visual_pressed:
        return 17 
    return type_index
