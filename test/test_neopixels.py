import time
from neopixels import set_niveau, off, NIVEAUX

print("Test NeoPixels - 8 LEDs, meme couleur, niveau = nb de paires (2 LEDs)")
print("GPIO 27. Ctrl+C pour quitter.")
print("-" * 40)

while True:
    for n in range(NIVEAUX + 1):
        set_niveau(n)
        if n == 0:
            print("Niveau 0 - tout eteint")
        else:
            print("Niveau %d - %d LEDs (meme couleur)" % (n, n * 2))
        time.sleep(1.5)
    print("--- cycle ---")

