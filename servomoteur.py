from machine import Pin, PWM
import time

PIN_SERVO = 28           

servo = PWM(Pin(PIN_SERVO))
servo.freq(50)

def set_servo_angle(angle):
    if angle < 0: angle = 0
    if angle > 180: angle = 180

    min_duty = 1638 
    max_duty = 8192
    
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    servo.duty_u16(duty)

if __name__ == "__main__":
    print("=== TEST SERVO STANDARD (0-180°) ===")
    try:
        print("Initialisation à 0° #PorteFermée")
        set_servo_angle(0)
        time.sleep(1)
        while True:
            print("\n--- Cycle de test ---")
            print("Mouvement vers 180°...")
            for a in range(0, 181, 10):
                set_servo_angle(a)
                time.sleep(0.05)
            print("180°. Pause 2s. #PorteOuverte")
            time.sleep(2)
            print("Retour vers 0°...")
            set_servo_angle(0)
            print("0°. Pause 2s. #PorteFermée")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nArrêt d'urgence.")
        servo.deinit()
