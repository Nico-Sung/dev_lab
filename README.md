## Plateau Indigo – Porte de la Ligue Pokémon

[![MicroPython](https://img.shields.io/badge/MicroPython-v1.20+-blue.svg)](https://micropython.org)
[![Hardware](https://img.shields.io/badge/Hardware-Pico%20W-orange.svg)](https://www.raspberrypi.com)

Ce projet est un jeu type **Mastermind** tournant sur un **Raspberry Pi Pico** avec :

- un écran **TFT ST7735** (SPI),
- un **servomoteur** qui ouvre/ferme la porte de la Ligue,
- un bouton spécial pour le **mode visualisation**,
- une LED filament contrôlée en **PWM** pour indiquer la progression.

Le but : deviner une séquence de 4 types Pokémon sur 3 niveaux de difficulté. Si les 3 niveaux sont réussis, la porte s’ouvre (servo à 180°) et l’écran affiche **VICTOIRE !**.

---

## Structure des fichiers

- **`main.py`** : boucle principale du jeu (logique Mastermind, états, gestion des niveaux, LED, servo).
- **`button.py`** : lecture des 8 boutons GPIO (0–7) + bouton visualisation (GPIO 15, code 18).
- **`mastermind_ecran.py`** : dessin de l’interface sur l’écran ST7735 (écran d’accueil, niveaux, historique, victoire, mode visualisation).
- **`servomoteur.py`** : fonction `set_servo_angle(angle)` pour piloter le SG90 (GPIO 14).
- **`leds.py`** : gestion de la LED filament (GPIO 13) en PWM (pourcentage de luminosité + respiration en mode visualisation).
- **`visualisation.py`** : mode décoration / visualisation activé par le bouton sur GPIO 15.
- **`test/test_buttons.py`** : script de test des boutons + détection du bouton visualisation.
- **`test/neopixel_test.py`**, `test/servoleds.py`, `test/leds.py` : anciens scripts de test matériels (facultatifs).

---

## Matériel et branchements

- **Microcontrôleur** : Raspberry Pi Pico.
- **Écran TFT ST7735** :
    - `SCK` → GPIO 18
    - `MOSI` → GPIO 19
    - `CS` → GPIO 17
    - `DC` → GPIO 16
    - `RST` → GPIO 20
- **Servomoteur** :
    - Signal → GPIO 14
- **LED filament (PWM)** :
    - Signal → GPIO 13
- **Boutons de type** :
    - 8 boutons sur GPIO **0–7** (lecture dans `button.py`, mapping vers les 18 types Pokémon selon le niveau).
- **Bouton mode visualisation** :
    - GPIO **15** (détection d’un maintien de 3 secondes pour activer / quitter le mode).

---

## Règles du jeu

- Le jeu se joue en **3 niveaux** (`step = 1, 2, 3`) avec des pools de types de plus en plus grands.
- À chaque niveau :
    - une séquence **secrète** de 4 types est tirée sans doublons,
    - le joueur doit la deviner avec un nombre d’essais limité (`MAX_ATTEMPTS = 10`).
- Après chaque séquence saisie :
    - 2 = bien placé,
    - 1 = bon type mais mal placé,
    - 0 = pas dans le niveau,
    - ces informations sont affichées à l’écran et dans la console.
- Si le joueur réussit les 3 niveaux :
    - le servo passe à **180°**,
    - la LED est à **100 %**,
    - l’écran affiche **VICTOIRE !**.

---

## Affichage et modes

- **Écran d’accueil** : affiche les emplacements vides, les piliers de la Ligue et le texte « vies restantes = 10 ».
- **Écran de niveau** :
    - en haut : piliers allumés selon le niveau,
    - au centre : 4 cases pour la combinaison en cours,
    - en bas : feedback du dernier essai + « vies restantes = X ».
- **Mode visualisation** :
    - activé / désactivé par un maintien de **3 s** sur le bouton GPIO 15,
    - l’écran passe sur « MODE VISUALISATION / 3 s = mode jeu »,
    - la LED filament entre en mode respiration (animation PWM).

---

## LED filament (progression)

La LED sur GPIO 13 indique le **niveau actuel** :

- Avant et pendant le **niveau 1** : **25 %**
- Niveau **2** : **50 %**
- Niveau **3** : **75 %**
- Victoire finale : **100 %**

La fonction `set_filament_percent(pourcentage)` est utilisée dans `main.py` via `update_brightness_for_step(step)` et lors de la victoire.

En mode visualisation, la LED utilise `update_filament()` pour un effet de respiration, puis revient à la luminosité du niveau courant à la sortie.

---

## Commandes console (debug)

Dans `main.py`, la fonction `check_console_command()` permet quelques raccourcis depuis la console MicroPython :

- **`1` + Entrée** : passe directement au **niveau 1**.
- **`2` + Entrée** : passe directement au **niveau 2**.
- **`3` + Entrée** : passe directement au **niveau 3**.
- **`win` + Entrée** :
    - force la victoire,
    - servo à **180°**,
    - LED à **100 %**,
    - écran **VICTOIRE !**.

Ces commandes sont pratiques pour tester rapidement le comportement du servo, de la LED et des écrans sans refaire toute une partie.

---

## Lancement

1. Flasher MicroPython sur le Pico.
2. Copier tous les fichiers du dossier `dev_lab` sur le Pico (`main.py`, `button.py`, `mastermind_ecran.py`, `servomoteur.py`, `leds.py`, `visualisation.py`, etc.).
3. Redémarrer le Pico : le script `main.py` se lance automatiquement.
4. Utiliser les boutons pour jouer, et la console série pour les commandes de test (`1`, `2`, `3`, `win`) si besoin.
