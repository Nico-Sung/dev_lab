# 📟 Pico-Dashboard IoT

Système de contrôle embarqué haute densité basé sur **Raspberry Pi Pico W**, conçu pour le pilotage d'interface physique avec retour visuel et mécanique.

---

## 🛠 Spécifications du Projet

Ce dashboard centralise la gestion de 18 entrées numériques, un affichage LCD et un asservissement mécanique.

### 🧠 Cœur du Système
* **Microcontrôleur :** Raspberry Pi Pico W (RP2040).
* **Connectivité :** Wi-Fi 2.4GHz intégré pour télémétrie et contrôle distant.

### 🖥 Interface & Sorties
* **Écran :** LCD TFT 1.44" (Driver `ST7735`, protocole SPI).
* **Actionneur :** 1x Servomoteur SG90 (Pilotage via PWM).

### ⌨️ Entrées Utilisateur
* **Matrice :** 18 boutons poussoirs configurés en entrées digitales.
* **Gestion :** Résistances de Pull-up internes activées pour minimiser le câblage.
