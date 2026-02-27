import time
from machine import Pin
from button import poll_buttons
from mastermind_ecran import draw_visual_mode, draw_visual_mode_door_open
from leds import update_filament, filament_off
from servomoteur import set_servo_angle

VISUALISATION_BUTTON = 18
SECRET_GPIO = 0
SECRET_HOLD_MS = 3000

secret_btn = Pin(SECRET_GPIO, Pin.IN, Pin.PULL_UP)
secret_last = 1
secret_hold_start = None
secret_triggered = False
door_open = False


def run_visualisation(tft, type_colors):
    global secret_last, secret_hold_start, secret_triggered, door_open
    draw_visual_mode(tft, 0, type_colors)
    secret_hold_start = None
    secret_triggered = False
    door_open = False
    secret_last = 1
    while True:
        update_filament()
        btn = poll_buttons(1)
        if btn == VISUALISATION_BUTTON:
            filament_off()
            return
        v = secret_btn.value()
        if v == 0:
            if secret_last == 1:
                secret_hold_start = time.ticks_ms()
                secret_triggered = False
            elif secret_hold_start is not None and not secret_triggered:
                if time.ticks_diff(time.ticks_ms(), secret_hold_start) >= SECRET_HOLD_MS:
                    if door_open:
                        set_servo_angle(0)
                        door_open = False
                        draw_visual_mode(tft, 0, type_colors)
                    else:
                        set_servo_angle(180)
                        door_open = True
                        draw_visual_mode_door_open(tft, type_colors)
                    secret_triggered = True
        else:
            secret_hold_start = None
            secret_triggered = False
        secret_last = v
        time.sleep(0.02)
