## Plateau Indigo – Porte de la Ligue Pokémon

[![MicroPython](https://img.shields.io/badge/MicroPython-v1.20+-blue.svg)](https://micropython.org)
[![Hardware](https://img.shields.io/badge/Hardware-Pico-orange.svg)](https://www.raspberrypi.com)

Ce projet est un jeu type **Mastermind** tournant sur un **Raspberry Pi Pico** avec :

- un écran **TFT ILI9341** (SPI, 240×320),
- un **servomoteur** qui ouvre/ferme la porte de la Ligue,
- un bouton dédié au **mode visualisation**,
- une LED filament contrôlée en **PWM** pour indiquer la progression.

Le but : deviner une séquence de 4 types Pokémon sur **3 niveaux** de difficulté. Si les 3 niveaux sont réussis, la porte s’ouvre (servo à **90°**) et l’écran affiche **VICTOIRE !**.

---

## Structure des fichiers

### Fichiers principaux (à copier sur le Pico)

| Fichier                   | Rôle                                                                         |
| ------------------------- | ---------------------------------------------------------------------------- |
| **`main.py`**             | Boucle principale du jeu (logique Mastermind, états, niveaux, LED, servo).   |
| **`ili9341.py`**          | Driver SPI de l’écran ILI9341.                                               |
| **`mastermind_ecran.py`** | Interface graphique (accueil, niveaux, historique, victoire, visualisation). |
| **`button.py`**           | Lecture des 8 boutons GPIO (0–7) et du bouton visualisation (GPIO 15).       |
| **`servomoteur.py`**      | Pilotage du servo SG90 sur GPIO 14.                                          |
| **`leds.py`**             | LED filament sur GPIO 13 (PWM + respiration en visualisation).               |
| **`visualisation.py`**    | Mode décoration activé par le bouton GPIO 15.                                |

### Scripts de test (facultatifs)

| Fichier                                                                  | Rôle                                                                                         |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| **`test_ecran.py`**                                                      | Test rapide de l’écran ILI9341 (remplissage de couleurs).                                    |
| **`test/test_buttons.py`**                                               | Test des boutons et du maintien GPIO 15.                                                     |
| **`test/servoleds.py`**, **`test/leds.py`**, **`test/neopixel_test.py`** | Anciens scripts de test — **ne plus utiliser** comme référence matérielle (config obsolète). |

### Fichiers legacy

- **`st7735.py`** : ancien driver pour écran ST7735, conservé pour référence mais **non utilisé** par `main.py`.
- Les fichiers à la racine du repo (**`/main.py`**, **`/button.py`**) sont des versions historiques.
  Pour la version active du projet, utiliser les fichiers dans **`dev_lab/`** et exécuter **`dev_lab/main.py`**.

---

## Matériel et branchements

- **Microcontrôleur** : Raspberry Pi Pico (MicroPython).

### Écran TFT ILI9341

| Signal écran          | GPIO Pico                            |
| --------------------- | ------------------------------------ |
| `SCK`                 | **18**                               |
| `MOSI`                | **19**                               |
| `CS`                  | **16**                               |
| `DC`                  | **21**                               |
| `RST`                 | **20**                               |
| `VCC`                 | **3,3 V**                            |
| `GND`                 | **GND**                              |
| `BL` (rétroéclairage) | **3,3 V** (si présent sur le module) |

### Autres composants

| Composant                | Branchement                                       |
| ------------------------ | ------------------------------------------------- |
| **Servomoteur** (signal) | GPIO **14**                                       |
| **LED filament** (PWM)   | GPIO **13**                                       |
| **8 boutons de type**    | GPIO **0 à 7** (pull-up interne, bouton vers GND) |
| **Bouton visualisation** | GPIO **15** (maintien 3 s pour activer / quitter) |

### Boutons multiplexés

Les 8 boutons physiques couvrent les types Pokémon disponibles selon le **niveau en cours** :

| GPIO | Étape 1 | Étape 2 | Étape 3 |
| ---- | ------- | ------- | ------- |
| 0    | Normal  | Electrik | Psy    |
| 1    | Feu     | Glace    | Insecte |
| 2    | Eau     | Combat   | Roche   |
| 3    | Plante  | Poison   | Spectre |
| 4    | Sol     | Dragon   | Dragon  |
| 5    | Vol     | Tenebres | Tenebres |
| 6    | Acier   | Acier    | Acier   |
| 7    | Fee     | Fee      | Fee     |

Ce mapping correspond à `button.py` via `GPIO_TO_TYPE_BY_STEP`. Quand une GPIO a moins de modes (ex. GPIO 6 et 7), son type est conservé aux étapes supérieures.

---

## Règles du jeu

- Le jeu se joue en **3 niveaux** avec des pools de types de plus en plus grands :
    - **Niveau 1** : 4 types (Normal, Feu, Eau, Plante)
    - **Niveau 2** : 6 types (Electrik, Glace, Combat, Poison, Sol, Vol)
    - **Niveau 3** : 8 types (Psy, Insecte, Roche, Spectre, Dragon, Tenebres, Acier, Fee)
- À chaque niveau :
    - une séquence **secrète** de 4 types est tirée **sans doublons**,
    - le joueur dispose de **8 essais** (`MAX_ATTEMPTS = 8`).
- Après chaque tentative complète :
    - **2** = bien placé (vert),
    - **1** = bon type mais mal placé (orange),
    - **0** = pas dans le niveau (rouge),
    - le feedback est affiché à l’écran et dans la console.
- En cas d’échec (0 essai restant) : une **nouvelle séquence** est générée pour le même niveau.
- Si le joueur réussit les **3 niveaux** :
    - le servo passe à **90°**,
    - la LED passe à **100 %**,
    - l’écran affiche **VICTOIRE !**.

---

## Affichage et modes

L’interface est dessinée en résolution **128×160** puis mise à l’échelle au centre de l’écran ILI9341 (240×320).

- **Écran d’accueil** : piliers, emplacements vides, texte « appuie pour lancer » et « vies restantes : 8 ».
- **Écran de niveau** :
    - en haut : piliers allumés selon le niveau,
    - au centre : séquence en cours et historique des 4 derniers essais,
    - en bas : feedback du dernier essai (vert / orange / rouge) et vies restantes.
- **Écran victoire** : message de réussite, porte ouverte.
- **Mode visualisation** :
    - activé / désactivé par un **maintien de 3 s** sur GPIO **15**,
    - l’écran affiche « MODE VISUALISATION / 3 s = mode jeu »,
    - la LED filament entre en mode **respiration** (PWM),
    - **easter egg** : en mode visualisation, maintenir **3 s** sur le bouton GPIO **0** ouvre ou ferme la porte manuellement.

---

## LED filament (progression)

La LED sur GPIO 13 indique le **niveau actuel** :

| État     | Luminosité |
| -------- | ---------- |
| Niveau 1 | **25 %**   |
| Niveau 2 | **50 %**   |
| Niveau 3 | **75 %**   |
| Victoire | **100 %**  |

En mode visualisation, `update_filament()` produit un effet de respiration. À la sortie du mode, la luminosité revient à celle du niveau en cours.

---

## Commandes console (debug)

Depuis la console série MicroPython, `main.py` accepte les commandes suivantes (saisir la commande puis Entrée) :

| Commande   | Effet                                                      |
| ---------- | ---------------------------------------------------------- |
| **`1`**    | Passe directement au niveau 1.                             |
| **`2`**    | Passe directement au niveau 2.                             |
| **`3`**    | Passe directement au niveau 3.                             |
| **`win`**  | Force la victoire (servo 90°, LED 100 %, écran victoire).  |
| **`demo`** | Affiche un écran de démo avec historique d’essais fictifs. |

Ces commandes permettent de tester rapidement le servo, la LED et l’interface sans jouer une partie complète.

---

## Lancement

1. Flasher **MicroPython** sur le Pico.
2. Copier sur le Pico les fichiers principaux :
    - `main.py`
    - `ili9341.py`
    - `mastermind_ecran.py`
    - `button.py`
    - `servomoteur.py`
    - `leds.py`
    - `visualisation.py`
3. Redémarrer le Pico : `main.py` se lance automatiquement.
4. Jouer avec les boutons GPIO 0–7, ou utiliser la console série pour les commandes de debug.

### Test de l’écran seul

Copier `test_ecran.py` et `ili9341.py` sur le Pico, puis l’exécuter.  
**Attention** : `test_ecran.py` utilise `CS = GPIO 17`. La config de référence du projet est **`CS = GPIO 16`** (comme dans `main.py`). Adapter si besoin.
