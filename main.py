from machine import Pin, SPI
import time
import urandom
from dev_lab.st7735 import ST7735
from button import poll as poll_buttons, types as button_types
from servomoteur import set_servo_angle
from mastermind_ecran import (
    draw_etape_screen,
    draw_success_screen,
    draw_visual_mode,
    draw_idle_screen,
)

spi = SPI(0, baudrate=20_000_000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19))
tft = ST7735(spi=spi, cs=17, dc=16, rst=20)

type_colors = [
    (255, 255, 255), (255, 80, 0), (0, 120, 255), (0, 200, 80),
    (255, 255, 0), (180, 220, 255), (200, 80, 60), (160, 60, 160),
    (180, 140, 80), (160, 200, 255), (255, 120, 180), (140, 180, 60),
    (160, 140, 100), (120, 80, 160), (120, 100, 255), (80, 60, 100),
    (180, 180, 200), (255, 180, 255),
]

POOL_SIZES = (4, 6, 8)
MAX_ATTEMPTS = 10
SEQ_LEN = 4
VISUAL_BUTTON = 17 


def mastermind_feedback(secret, guess):
    good = sum(1 for i in range(SEQ_LEN) if guess[i] == secret[i])
    rest = [secret[i] for i in range(SEQ_LEN) if guess[i] != secret[i]]
    wrong = 0
    for i in range(SEQ_LEN):
        if guess[i] != secret[i] and guess[i] in rest:
            wrong += 1
            rest.remove(guess[i])
    return good, wrong


def new_secret(pool_size):
    indices = list(range(pool_size))
    result = []
    for _ in range(SEQ_LEN):
        i = urandom.getrandbits(8) % len(indices)
        result.append(indices[i])
        indices.pop(i)
    return result


phase = "idle"  
step = 1
secret = []
guess = [None, None, None, None]
current_slot = 0
attempts_left = MAX_ATTEMPTS
last_good, last_wrong = 0, 0
visual_frame = 0
long_press_threshold = 1.2 

set_servo_angle(0)
draw_idle_screen(tft, 1, 3)
print("Plateau Indigo - Choisis un type pour commencer. Long press Fee = mode visuel.")

while True:
    btn = poll_buttons()
    now = time.time()

    if btn is not None:
        type_name = button_types[btn] if btn < len(button_types) else "?"
        print("[Bouton %d] %s" % (btn, type_name))

    if phase == "visual":
        draw_visual_mode(tft, visual_frame, type_colors)
        visual_frame += 1
        if btn == VISUAL_BUTTON:
            phase = "idle"
            draw_idle_screen(tft, 1, 3)
            print("Mode visuel quitté.")
        time.sleep(0.25)
        continue

    if btn == VISUAL_BUTTON:
        t0 = now
        while poll_buttons() == VISUAL_BUTTON and (time.time() - t0) < long_press_threshold:
            time.sleep(0.05)
        if time.time() - t0 >= long_press_threshold:
            phase = "visual"
            visual_frame = 0
            print("Mode visuel (déco) activé.")
            continue
        time.sleep(0.02)
        continue

    if phase == "success":
        if btn is not None:
            phase = "idle"
            step = 1
            set_servo_angle(0)
            draw_idle_screen(tft, 1, 3)
            print("Nouvelle partie.")
        time.sleep(0.1)
        continue

    if phase == "idle":
        if btn is not None and btn < POOL_SIZES[0]:
            phase = "play"
            step = 1
            pool_size = POOL_SIZES[step - 1]
            secret = new_secret(pool_size)
            guess = [btn, None, None, None]
            current_slot = 1
            attempts_left = MAX_ATTEMPTS
            last_good, last_wrong = 0, 0
            draw_etape_screen(tft, step, 3, guess, 0, 0, attempts_left, type_colors, pool_size)
            print("Étape 1/3 - Slot 1: %s" % button_types[btn])
        time.sleep(0.02)
        continue

    pool_size = POOL_SIZES[step - 1]
    if btn is not None:
        if btn == VISUAL_BUTTON:
            pass
        elif btn < pool_size:
            guess[current_slot] = btn
            current_slot += 1
            draw_etape_screen(tft, step, 3, guess, last_good, last_wrong, attempts_left, type_colors, pool_size)
            print("Étape %d/3 - Slot %d: %s" % (step, current_slot, button_types[btn]))

            if current_slot >= SEQ_LEN:
                good, wrong = mastermind_feedback(secret, guess)
                last_good, last_wrong = good, wrong
                attempts_left -= 1
                draw_etape_screen(tft, step, 3, guess, good, wrong, attempts_left, type_colors, pool_size)
                print("  -> Bien placé: %d, Mal placé: %d | Essais restants: %d" % (good, wrong, attempts_left))
                time.sleep(0.8)

                if good == SEQ_LEN:
                    time.sleep(0.5)
                    if step >= 3:
                        phase = "success"
                        set_servo_angle(180)
                        draw_success_screen(tft)
                        print("Ligue ouverte ! Récompense.")
                    else:
                        step += 1
                        pool_size = POOL_SIZES[step - 1]
                        secret = new_secret(pool_size)
                        guess = [None, None, None, None]
                        current_slot = 0
                        attempts_left = MAX_ATTEMPTS
                        last_good, last_wrong = 0, 0
                        draw_etape_screen(tft, step, 3, guess, 0, 0, attempts_left, type_colors, pool_size)
                        print("Étape %d/3 - Séquences à deviner (pool %d types)." % (step, pool_size))
                elif attempts_left <= 0:
                    secret = new_secret(pool_size)
                    guess = [None, None, None, None]
                    current_slot = 0
                    attempts_left = MAX_ATTEMPTS
                    last_good, last_wrong = 0, 0
                    draw_etape_screen(tft, step, 3, guess, 0, 0, attempts_left, type_colors, pool_size)
                    print("Échec étape %d - Nouvelle séquence." % step)
                else:
                    guess = [None, None, None, None]
                    current_slot = 0
                    draw_etape_screen(tft, step, 3, guess, 0, 0, attempts_left, type_colors, pool_size)

    else:
        draw_etape_screen(tft, step, 3, guess, last_good, last_wrong, attempts_left, type_colors, pool_size)

    time.sleep(0.02)

