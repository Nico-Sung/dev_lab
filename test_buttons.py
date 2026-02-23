# Test de tous les boutons (18 types)

from machine import Pin
from button import buttons, types as button_types, poll

print("=== Test des boutons ===")
print("Appuyez sur les boutons (0-17). Ctrl+C pour quitter.")
print("-" * 30)

while True:
    idx = poll()
    if idx is not None:
        name = button_types[idx] if idx < len(button_types) else "?"
        print("Bouton %2d -> %s" % (idx, name))