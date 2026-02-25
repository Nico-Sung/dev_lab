import time
import urandom
from machine import Pin, PWM, SPI, Timer
import neopixel

# ==========================================
# IMPORTS DES MODULES EXTERNES
# ==========================================
from st7735 import ST7735
from button import poll as poll_buttons, types as button_types
from mastermind_ecran import (
    draw_etape_screen,
    draw_success_screen,
    draw_idle_screen,
)

# ==========================================
# 1. CONFIGURATION MATÉRIELLE
# ==========================================

# --- NeoPixel (LED RGB) ---
PIN_NEO = 27
NUM_LEDS = 1
np = neopixel.NeoPixel(Pin(PIN_NEO), NUM_LEDS)

def set_led(r, g, b):
    """Change la couleur de la LED NeoPixel."""
    np[0] = (r, g, b)
    np.write()

# --- Servo Moteur & Mouvement Continu ---
PIN_SERVO = 28
servo = PWM(Pin(PIN_SERVO))
servo.freq(50)

def set_servo_angle(angle):
    """Positionne le servo entre 0 et 180 degrés."""
    if angle < 0: angle = 0
    if angle > 180: angle = 180
    
    min_duty = 1638 
    max_duty = 8192
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    servo.duty_u16(duty)

# Variables pour le balayage continu du servo
current_angle = 0
direction = 2  # Le servo avancera de 2° à chaque tick

def move_servo_continuous(timer):
    """Fonction appelée par le Timer en arrière-plan pour faire balayer le servo."""
    global current_angle, direction
    current_angle += direction
    
    # Inversion de la direction quand on atteint les limites
    if current_angle >= 180:
        current_angle = 180
        direction = -2
    elif current_angle <= 0:
        current_angle = 0
        direction = 2
        
    set_servo_angle(current_angle)

# Création du Timer (sans le démarrer tout de suite)
servo_timer = Timer(-1)

# --- Écran TFT ST7735 ---
spi = SPI(0, baudrate=20_000_000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19))
tft = ST7735(spi=spi, cs=17, dc=16, rst=20)


# ==========================================
# 2. CONSTANTES ET LOGIQUE DU JEU
# ==========================================

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

def mastermind_feedback_peg(secret, guess):
    """Calcule le score Mastermind: 2 = Bien placé, 1 = Bonne couleur/Mal placé."""
    used_secret = [False] * SEQ_LEN
    used_guess = [False] * SEQ_LEN
    feedback = [0] * SEQ_LEN
    
    # Vérification des pions bien placés
    for i in range(SEQ_LEN):
        if guess[i] == secret[i]:
            feedback[i] = 2
            used_secret[i] = used_guess[i] = True
            
    # Vérification des pions mal placés
    for i in range(SEQ_LEN):
        if used_guess[i]:
            continue
        for j in range(SEQ_LEN):
            if not used_secret[j] and secret[j] == guess[i]:
                feedback[i] = 1
                used_secret[j] = True
                break
    return feedback

def new_secret(pool_size):
    """Génère une nouvelle séquence secrète sans doublons."""
    indices = list(range(pool_size))
    result = []
    for _ in range(SEQ_LEN):
        i = urandom.getrandbits(8) % len(indices)
        result.append(indices[i])
        indices.pop(i)
    return result


# ==========================================
# 3. INITIALISATION DU JEU
# ==========================================

phase = "idle"  
step = 1
secret = []
guess = [None, None, None, None]
current_slot = 0
attempts_left = MAX_ATTEMPTS
last_feedback = [0, 0, 0, 0]  
history = []

# Mise en place de l'état initial
set_led(0, 0, 50)  # LED Bleu faible (Idle)
draw_idle_screen(tft, 1, 3)

# Démarrage du mouvement continu du servo (tick toutes les 20 ms)
servo_timer.init(period=20, mode=Timer.PERIODIC, callback=move_servo_continuous)
print("Plateau Indigo - Prêt. Le servo tourne !")


# ==========================================
# 4. BOUCLE PRINCIPALE
# ==========================================

while True:
    btn = poll_buttons()
    
    if btn is not None:
        type_name = button_types[btn] if btn < len(button_types) else "?"
        print(f"[Bouton {btn}] {type_name}")

    # --- PHASE: SUCCESS (Gagné, récompense délivrée) ---
    if phase == "success":
        set_led(0, 255, 0) # LED Verte fixe
        
        if btn is not None:
            # Un bouton a été pressé, on relance une partie
            phase = "idle"
            step = 1
            
            # On relance le Timer pour que le servo se remette à balayer
            servo_timer.init(period=20, mode=Timer.PERIODIC, callback=move_servo_continuous)
            
            set_led(0, 0, 50) # Retour LED Bleu
            draw_idle_screen(tft, 1, 3)
            print("Nouvelle partie.")
            
        time.sleep(0.1)
        continue

    # --- PHASE: IDLE (Attente démarrage) ---
    if phase == "idle":
        if btn is not None and btn < POOL_SIZES[0]:
            phase = "play"
            step = 1
            pool_size = POOL_SIZES[step - 1]
            secret = new_secret(pool_size)
            guess = [btn, None, None, None]
            current_slot = 1
            attempts_left = MAX_ATTEMPTS
            last_feedback = [0, 0, 0, 0]
            history = []
            
            set_led(255, 100, 0) # LED Orange (Partie en cours)
            draw_etape_screen(tft, step, 3, guess, last_feedback, attempts_left, type_colors, pool_size, history)
            print(f"Étape 1/3 - Slot 1: {button_types[btn]}")
            
        time.sleep(0.02)
        continue

    # --- PHASE: PLAY (Jeu en cours) ---
    pool_size = POOL_SIZES[step - 1]
    
    if btn is not None:
        if btn < pool_size:
            guess[current_slot] = btn
            current_slot += 1
            draw_etape_screen(tft, step, 3, guess, last_feedback, attempts_left, type_colors, pool_size, history)
            print(f"Étape {step}/3 - Slot {current_slot}: {button_types[btn]}")

            # Si on a entré les 4 couleurs, on vérifie la combinaison
            if current_slot >= SEQ_LEN:
                feedback_peg = mastermind_feedback_peg(secret, guess)
                last_feedback = feedback_peg
                history.append((list(guess), list(feedback_peg)))
                history = history[-4:] # Conserve uniquement l'historique récent
                attempts_left -= 1
                
                draw_etape_screen(tft, step, 3, guess, feedback_peg, attempts_left, type_colors, pool_size, history)
                
                good = sum(1 for f in feedback_peg if f == 2)
                wrong = sum(1 for f in feedback_peg if f == 1)
                print(f" -> Bien: {good}, Mal: {wrong} | Essais: {attempts_left}")
                
                # Animation visuelle LED rapide
                if good == SEQ_LEN:
                    set_led(0, 255, 0) # Vert flash (Gagné l'étape)
                else:
                    set_led(255, 0, 0) # Rouge flash (Séquence incorrecte)
                
                time.sleep(0.8)
                set_led(255, 100, 0) # Retour Orange

                # Logique: Combinaison trouvée !
                if good == SEQ_LEN:
                    time.sleep(0.5)
                    
                    if step >= 3:
                        # VICTOIRE FINALE
                        phase = "success"
                        
                        # On coupe le timer du servo et on ouvre la porte à 180°
                        servo_timer.deinit() 
                        set_servo_angle(180) 
                        
                        draw_success_screen(tft)
                        print("Ligue ouverte ! Récompense.")
                    else:
                        # PASSAGE À L'ÉTAPE SUIVANTE
                        step += 1
                        pool_size = POOL_SIZES[step - 1]
                        secret = new_secret(pool_size)
                        guess = [None, None, None, None]
                        current_slot = 0
                        attempts_left = MAX_ATTEMPTS
                        last_feedback = [0, 0, 0, 0]
                        history = []
                        draw_etape_screen(tft, step, 3, guess, last_feedback, attempts_left, type_colors, pool_size, history)
                        print(f"Étape {step}/3 - Nouvelle séquence.")
                
                # Logique: Plus d'essais, on recommence l'étape
                elif attempts_left <= 0:
                    set_led(255, 0, 0) # Rouge fixe
                    time.sleep(0.5)
                    secret = new_secret(pool_size)
                    guess = [None, None, None, None]
                    current_slot = 0
                    attempts_left = MAX_ATTEMPTS
                    last_feedback = [0, 0, 0, 0]
                    history = []
                    draw_etape_screen(tft, step, 3, guess, last_feedback, attempts_left, type_colors, pool_size, history)
                    print(f"Échec étape {step} - Reset de la séquence.")
                    set_led(255, 100, 0) # Retour Orange
                
                # Logique: Continuer l'étape en cours
                else:
                    guess = [None, None, None, None]
                    current_slot = 0
                    draw_etape_screen(tft, step, 3, guess, last_feedback, attempts_left, type_colors, pool_size, history)

    time.sleep(0.02)