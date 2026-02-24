# Écran Mastermind - Plateau Indigo / Porte de la Ligue Pokémon

from st7735 import color565


INDIGO_BG = color565(25, 25, 65)
PILLAR_OFF = color565(50, 50, 75)
PILLAR_ON = color565(255, 200, 80)
DOOR = color565(90, 55, 35)
DOOR_LINE = color565(60, 40, 25)
SLOT_BORDER = color565(100, 100, 130)
SLOT_EMPTY = color565(40, 40, 60)
FEEDBACK_GOOD = color565(0, 255, 100)   
FEEDBACK_WRONG = color565(255, 220, 0)  
FEEDBACK_BAD = color565(244, 67, 50)   
TITLE = color565(180, 180, 220)
SUCCESS_GOLD = color565(255, 215, 0)


def draw_background(tft):
    """Fond indigo."""
    tft.fill(INDIGO_BG)


def draw_pillars(tft, step_done):
    """q
    Dessine les 3 piliers du chemin (séquence d'arrivée).
    step_done: 0, 1, 2 ou 3 = nombre d'étapes réussies (piliers allumés).
    """
    w, h = 32, 22
    gap = 6
    y = 6
    for i in range(3):
        x = 8 + i * (w + gap)
        color = PILLAR_ON if i < step_done else PILLAR_OFF
        tft.fill_rect(x, y, w, h, color)


def draw_door(tft, open_):
    """
    Porte de la Ligue : fermée = un bloc ; ouverte = deux battants écartés.
    """
    door_h = 38
    y = 118
    if open_:
        tft.fill_rect(4, y, 28, door_h, DOOR)
        tft.fill_rect(4 + 28, y, 4, door_h, DOOR_LINE)
        tft.fill_rect(96, y, 28, door_h, DOOR)
        tft.fill_rect(96 - 4, y, 4, door_h, DOOR_LINE)
    else:
        tft.fill_rect(24, y, 80, door_h, DOOR)
        tft.fill_rect(62, y, 4, door_h, DOOR_LINE)


def draw_guess_slots(tft, guess, type_colors, pool_count):
    """
    Affiche les 4 emplacements de la tentative (types ou vides).
    guess: liste de 4 (type_idx or None)
    """
    slot_size = 24
    gap = 4
    y = 34
    for i in range(4):
        x = 8 + i * (slot_size + gap)
        tft.fill_rect(x - 1, y - 1, slot_size + 2, slot_size + 2, SLOT_BORDER)
        if guess[i] is not None and guess[i] < len(type_colors):
            c = type_colors[guess[i]]
            if isinstance(c, (list, tuple)):
                col = color565(c[0], c[1], c[2])
            else:
                col = c
            tft.fill_rect(x, y, slot_size, slot_size, col)
        else:
            tft.fill_rect(x, y, slot_size, slot_size, SLOT_EMPTY)


def _feedback_color(fb):
    """fb: 0=rouge, 1=jaune, 2=vert."""
    if fb == 2:
        return FEEDBACK_GOOD
    if fb == 1:
        return FEEDBACK_WRONG
    return FEEDBACK_BAD


# Historique : 5 essais à gauche, 5 à droite (carrés réduits pour tenir sur les côtés)
HISTORY_LEFT_ROWS = 5
HISTORY_RIGHT_ROWS = 5

def _draw_history_column(tft, rows, type_colors, x_start, y_start, row_h, row_margin, box_size, box_gap, dot):
    """Dessine une colonne d'historique (5 lignes max)."""
    for row_idx, (g, feedback_peg) in enumerate(rows):
        y = y_start + row_idx * (row_h + row_margin)
        for i in range(4):
            x = x_start + i * (box_size + box_gap)
            if g[i] is not None and g[i] < len(type_colors):
                c = type_colors[g[i]]
                if isinstance(c, (list, tuple)):
                    col = color565(c[0], c[1], c[2])
                else:
                    col = c
                tft.fill_rect(x, y, box_size, row_h, col)
            else:
                tft.fill_rect(x, y, box_size, row_h, SLOT_EMPTY)
        x_dots = x_start + 4 * (box_size + box_gap) + box_gap
        for i in range(4):
            xx = x_dots + i * (dot + 1)
            fb = feedback_peg[i] if i < len(feedback_peg) else 0
            tft.fill_rect(xx, y + (row_h - dot) // 2, dot, dot, _feedback_color(fb))


def draw_history(tft, history, type_colors):
    """
    Affiche 10 essais : 5 à gauche, 5 à droite.
    Gauche = essais 1 à 5, droite = essais 6 à 10.
    """
    row_h = 6
    row_margin = 2
    box_size = 5
    box_gap = 1
    dot = 3
    y_start = 62
    last_10 = history[-10:]
    left_rows = last_10[:5]
    right_rows = last_10[5:]
    col_width = 4 * (box_size + box_gap) + box_gap + 4 * (dot + 1)
    x_left = 4
    x_right = 128 - 4 - col_width
    _draw_history_column(tft, left_rows, type_colors, x_left, y_start, row_h, row_margin, box_size, box_gap, dot)
    _draw_history_column(tft, right_rows, type_colors, x_right, y_start, row_h, row_margin, box_size, box_gap, dot)


def draw_feedback(tft, feedback_peg):
    """
    Indicateurs Mastermind par emplacement : vert = bon, jaune = mal placé, rouge = pas dans la séquence.
    feedback_peg: liste de 4 (0=rouge, 1=jaune, 2=vert).
    """
    dot_size = 8
    # Sous l'historique (5 lignes × (6+2)px de chaque côté → jusqu'à y=102)
    y = 106
    x_start = 28
    gap = 6
    for i in range(4):
        x = x_start + i * (dot_size + gap)
        fb = feedback_peg[i] if i < len(feedback_peg) else 0
        tft.fill_rect(x, y, dot_size, dot_size, _feedback_color(fb))


def draw_step_indicator(tft, step, total, attempts_left):
    """
    Indicateur d'étape et d'essais (visuel simple : barre ou pastilles).
    step: 1..total, attempts_left: essais restants.
    """
    max_attempts = 5
    dot = 4
    y = 30
    for i in range(max_attempts):
        x = 108 + (i % 2) * 6
        yy = y + (i // 2) * 6
        if i < (max_attempts - attempts_left):
            tft.fill_rect(x, yy, dot, dot, FEEDBACK_WRONG) 
        else:
            tft.fill_rect(x, yy, dot, dot, PILLAR_OFF) 


def draw_etape_screen(tft, step, total, guess, feedback_peg, attempts_left, type_colors, pool_count, history=None):
    """Écran de jeu : piliers, slots, historique des essais, feedback vert/jaune/rouge, porte fermée."""
    draw_background(tft)
    draw_pillars(tft, step - 1)  
    draw_guess_slots(tft, guess, type_colors, pool_count)
    if history:
        draw_history(tft, history, type_colors)
    draw_feedback(tft, feedback_peg)
    draw_step_indicator(tft, step, total, attempts_left)
    draw_door(tft, False)


def draw_success_screen(tft):
    """Portes ouvertes, tous les piliers allumés."""
    draw_background(tft)
    draw_pillars(tft, 3)
    draw_door(tft, True)
    tft.fill_rect(10, 78, 108, 28, SUCCESS_GOLD)
    tft.fill_rect(14, 82, 100, 20, INDIGO_BG)


def draw_visual_mode(tft, frame, type_colors):
    """
    Mode déco : piliers qui s'illuminent en cycle, pas de jeu.
    frame: numéro d'animation (incrémenté à chaque appel).
    """
    draw_background(tft)
    pillar_lit = frame % 4
    if pillar_lit < 3:
        draw_pillars(tft, pillar_lit + 1)
    else:
        draw_pillars(tft, 3)
    draw_door(tft, False)


def draw_idle_screen(tft, step, total, attempts_left=5):
    """Écran d'attente : titre / prêt à jouer."""
    draw_background(tft)
    draw_pillars(tft, 0)
    draw_door(tft, False)
    draw_guess_slots(tft, [None, None, None, None], [], 0)
    draw_feedback(tft, [0, 0, 0, 0])
    draw_step_indicator(tft, 1, total, attempts_left)

