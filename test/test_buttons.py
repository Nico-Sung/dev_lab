# Changer d'étape : touche 1, 2 ou 3 du clavier.

import time
import sys
from button import poll, types as button_types

def read_key():
    """Lit une touche si disponible (non bloquant). Retourne None ou le caractère."""
    try:
        import uselect
        poll_in = uselect.poll()
        poll_in.register(sys.stdin, uselect.POLLIN)
        if poll_in.poll(0):
            return sys.stdin.read(1)
    except (ImportError, OSError):
        pass
    try:
        import select
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
    except (ImportError, OSError):
        pass
    return None

step = 1
print("=== Test des boutons ===")
print("GPIO 0-7 = types. GPIO 15 = mode visualisation (maintenir 3 s).")
print("Changer d'étape : touches 1, 2 ou 3 du clavier.")
print("Étape actuelle: %d/3" % step)
print("-" * 40)

while True:
    k = read_key()
    if k in ("1", "2", "3"):
        step = int(k)
        print(">>> Étape %d/3" % step)

    result = poll(step)
    type_idx = result[0]
    visualisation_15 = result[1] if len(result) >= 2 else False
    if type_idx is not None:
        name = button_types[type_idx] if type_idx < len(button_types) else "?"
        print("Bouton type %2d -> %s" % (type_idx, name))
    if visualisation_15:
        print(">>> Mode visualisation (GPIO 15) OK")

    time.sleep(0.02)
