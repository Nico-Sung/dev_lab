from machine import Pin
import neopixel

PIN_NEO = 27
NUM_LEDS = 8
LEDS_PAR_NIVEAU = 2
NIVEAUX = NUM_LEDS // LEDS_PAR_NIVEAU

np = neopixel.NeoPixel(Pin(PIN_NEO), NUM_LEDS)

COULEUR_DEFAUT = (20, 45, 0)


def set_niveau(niveau, couleur=None):
    """
    Allume les NeoPixels par niveau : toutes les LEDs allumées ont la même couleur.
    niveau 0 = tout éteint, 1 = 2 LEDs, 2 = 4 LEDs, 3 = 6 LEDs, 4 = 8 LEDs.
    couleur = (r, g, b) ou None pour la couleur par défaut.
    """
    if couleur is None:
        couleur = COULEUR_DEFAUT
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    nb_allumees = min(niveau * LEDS_PAR_NIVEAU, NUM_LEDS)
    for i in range(nb_allumees):
        np[i] = couleur
    np.write()


def off():
    set_niveau(0)

