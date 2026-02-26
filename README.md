# 📟 Pico-Dashboard IoT

[![MicroPython](https://img.shields.io/badge/MicroPython-v1.20+-blue.svg)](https://micropython.org)
[![Hardware](https://img.shields.io/badge/Hardware-Pico%20W-orange.svg)](https://www.raspberrypi.com)

## 📝 Description du Projet
Le **Pico-Dashboard IoT** est une interface de contrôle physique polyvalente conçue pour centraliser les interactions domotiques ou industrielles. Ce projet combine électronique de précision, développement MicroPython et design mécanique 3D.

L'objectif est de créer un boîtier autonome capable de gérer :
* **Saisie utilisateur massive :** 18 boutons poussoirs pour un contrôle direct et instantané.
* **Retour visuel dynamique :** Un écran TFT pour l'affichage de télémétrie, de menus ou d'états système.
* **Action mécanique :** Un servomoteur intégré permettant un retour physique (type indicateur à aiguille ou verrouillage).

---

## 🛠 Spécifications Techniques

### 🧠 Cœur & Connectivité
* **Microcontrôleur :** Raspberry Pi Pico W (RP2040 Dual-core).

### 🖥 Périphériques
* **Affichage :** LCD TFT 1.44" (Driver `ST7735`, protocole SPI).
* **Actionneur :** 1x Servomoteur SG90 (Pilotage via PWM).
* **Entrées :** 18 boutons poussoirs configurés avec Pull-up interne.

---

## 🔌 Branchements (Pinout)



| Composant | Pin Pico (GPIO) | Fonction |
| :--- | :--- | :--- |
| **Écran (SCL/SDA)** | GP18 / GP19 | Bus SPI |
| **Écran (DC/RES/CS)**| GP17 / GP20 / GP16 | Signal de contrôle |
| **Servomoteur** | GP | Signal PWM |
| **Boutons** | GP0 à GP7 + GP15 | Entrées Digitales |

---

## 🚀 Installation & Déploiement

1.  **Firmware :** Installez le dernier firmware [MicroPython](https://micropython.org/download/RPI_PICO_W/) sur votre Pico W.
2.  **Upload :** Transférez vos fichiers Python (drivers et main) via Thonny ou `mpremote`.
3.  **Validation :** Utilisez des scripts de test unitaires pour vérifier chaque composant (écran, servo, boutons) avant l'assemblage final.

---

## 📐 Conception 3D
Le boîtier est optimisé pour l'impression **FDM** (PLA ou PETG) :
* **Infill :** 15-20% pour un bon compromis poids/solidité.
* **Montage :** Emplacements boutons prévus pour un montage "press-fit".
* **Ergonomie :** Façade inclinée à 15° pour faciliter la lecture de l'écran et l'accès aux boutons.
