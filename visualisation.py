import time
from button import poll_buttons
from mastermind_ecran import draw_visual_mode

VISUALISATION_BUTTON = 18


def run_visualisation(tft, type_colors):
    draw_visual_mode(tft, 0, type_colors)
    while True:
        btn = poll_buttons(1)
        if btn == VISUALISATION_BUTTON:
            return
        time.sleep(0.02)
