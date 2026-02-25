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
print("GPIO 0-7 = types selon l'étape.")
print("Changer d'étape : touches 1, 2 ou 3 du clavier.")
print("Étape actuelle: %d/3" % step)
print("-" * 40)

while True:
    k = read_key()
    if k in ("1", "2", "3"):
        step = int(k)
        print(">>> Étape %d/3" % step)

    type_idx, _ = poll(step)
    if type_idx is not None:
        name = button_types[type_idx] if type_idx < len(button_types) else "?"
        print("Bouton type %2d -> %s" % (type_idx, name))

    time.sleep(0.02)
