from machine import Pin, SPI
import time
import urandom
from dev_lab.st7735 import ST7735
from button import poll_buttons, types as button_types
from servomoteur import set_servo_angle
from mastermind_ecran import (
    draw_etape_screen,
    draw_success_screen,
    draw_visual_mode,
    draw_idle_screen,
)

spi = SPI(0, baudrate=40_000_000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19))
tft = ST7735(spi=spi, cs=17, dc=16, rst=20)

type_colors = [
    (255, 255, 255), (255, 80, 0), (0, 120, 255), (0, 200, 80),
    (255, 255, 0), (180, 220, 255), (200, 80, 60), (160, 60, 160),
    (180, 140, 80), (160, 200, 255), (255, 120, 180), (140, 180, 60),
    (160, 140, 100), (120, 80, 160), (120, 100, 255), (80, 60, 100),
    (180, 180, 200), (255, 180, 255),
]

POOL_BY_STEP = [
    [0, 1, 2, 3],
    [4, 5, 6, 7, 8, 9],
    [10, 11, 12, 13, 14, 15, 16, 17],
]
POOL_SIZES = tuple(len(p) for p in POOL_BY_STEP)
MAX_ATTEMPTS = 10
SEQ_LEN = 4
VISUAL_BUTTON = 17 


def mastermind_feedback_peg(secret, guess):
    used_secret = [False] * SEQ_LEN
    used_guess = [False] * SEQ_LEN
    feedback = [0] * SEQ_LEN
    for i in range(SEQ_LEN):
        if guess[i] == secret[i]:
            feedback[i] = 2
            used_secret[i] = used_guess[i] = True
    for i in range(SEQ_LEN):
        if used_guess[i]:
            continue
        for j in range(SEQ_LEN):
            if not used_secret[j] and secret[j] == guess[i]:
                feedback[i] = 1
                used_secret[j] = True
                break
    return feedback


def new_secret(step):
    pool = list(POOL_BY_STEP[step - 1])
    result = []
    for _ in range(SEQ_LEN):
        i = urandom.getrandbits(8) % len(pool)
        result.append(pool[i])
        pool.pop(i)
    return result


phase = "idle"  
step = 1
secret = []
guess = [None, None, None, None]
current_slot = 0
attempts_left = MAX_ATTEMPTS
last_feedback = [0, 0, 0, 0]  
history = [] 
visual_frame = 0

set_servo_angle(0)
draw_idle_screen(tft, 1, 3)
print("Plateau Indigo - Choisis un type pour commencer. mode visuel = bouton 17.")

while True:
    btn = poll_buttons(step)
    now = time.time()

    if btn is not None and btn != VISUAL_BUTTON:
        type_name = button_types[btn] if btn < len(button_types) else "?"
        print("[Bouton %d] %s" % (btn, type_name))

    if phase == "visual":
        draw_visual_mode(tft, visual_frame, type_colors)
        visual_frame += 1
        if btn == VISUAL_BUTTON:
            phase = "idle"
            draw_idle_screen(tft, 1, 3)
            print("Mode visuel quitté.")
        time.sleep(0.08)
        continue

    if btn == VISUAL_BUTTON:
        phase = "visual"
        visual_frame = 0
        print("Mode visuel (déco) activé.")
        time.sleep(0.01)
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
        if btn is not None and btn in POOL_BY_STEP[0]:
            phase = "play"
            step = 1
            pool_size = POOL_SIZES[step - 1]
            secret = new_secret(step)
            guess = [btn, None, None, None]
            current_slot = 1
            attempts_left = MAX_ATTEMPTS
            last_feedback = [0, 0, 0, 0]
            history = []
            draw_etape_screen(tft, step, 3, guess, last_feedback, attempts_left, type_colors, pool_size, history)
            print("Étape 1/3 - Slot 1: %s" % button_types[btn])
        time.sleep(0.01)
        continue

    pool_size = POOL_SIZES[step - 1]
    if btn is not None:
        if btn == VISUAL_BUTTON:
            pass
        elif btn in POOL_BY_STEP[step - 1]:
            guess[current_slot] = btn
            current_slot += 1
            draw_etape_screen(tft, step, 3, guess, last_feedback, attempts_left, type_colors, pool_size, history)
            print("Étape %d/3 - Slot %d: %s" % (step, current_slot, button_types[btn]))

            if current_slot >= SEQ_LEN:
                feedback_peg = mastermind_feedback_peg(secret, guess)
                last_feedback = feedback_peg
                history.append((list(guess), list(feedback_peg)))
                history = history[-4:]
                attempts_left -= 1
                draw_etape_screen(tft, step, 3, guess, feedback_peg, attempts_left, type_colors, pool_size, history)
                good = sum(1 for f in feedback_peg if f == 2)
                wrong = sum(1 for f in feedback_peg if f == 1)
                print("  -> Bien placé: %d, Mal placé: %d | Essais restants: %d" % (good, wrong, attempts_left))
                time.sleep(0.8)

                if sum(1 for f in feedback_peg if f == 2) == SEQ_LEN:
                    time.sleep(0.5)
                    if step >= 3:
                        phase = "success"
                        set_servo_angle(180)
                        draw_success_screen(tft)
                        print("Ligue ouverte ! Récompense.")
                    else:
                        step += 1
                        pool_size = POOL_SIZES[step - 1]
                        secret = new_secret(step)
                        guess = [None, None, None, None]
                        current_slot = 0
                        attempts_left = MAX_ATTEMPTS
                        last_feedback = [0, 0, 0, 0]
                        history = []
                        draw_etape_screen(tft, step, 3, guess, last_feedback, attempts_left, type_colors, pool_size, history)
                        print("Étape %d/3 - Séquences à deviner (pool %d types)." % (step, pool_size))
                elif attempts_left <= 0:
                    secret = new_secret(step)
                    guess = [None, None, None, None]
                    current_slot = 0
                    attempts_left = MAX_ATTEMPTS
                    last_feedback = [0, 0, 0, 0]
                    history = []
                    draw_etape_screen(tft, step, 3, guess, last_feedback, attempts_left, type_colors, pool_size, history)
                    print("Échec étape %d - Nouvelle séquence." % step)
                else:
                    guess = [None, None, None, None]
                    current_slot = 0
                    draw_etape_screen(tft, step, 3, guess, last_feedback, attempts_left, type_colors, pool_size, history)

    time.sleep(0.01)

