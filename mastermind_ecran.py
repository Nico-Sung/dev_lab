from st7735 import color565


INDIGO_BG = color565(255, 255, 255)     
PILLAR_OFF = color565(220, 220, 225)     
PILLAR_ON = color565(255, 160, 0)        
DOOR = color565(120, 80, 50)            
DOOR_LINE = color565(80, 50, 30)         
SLOT_BORDER = color565(180, 180, 180)   
SLOT_EMPTY = color565(240, 240, 240)     
FEEDBACK_GOOD = color565(0, 180, 80)     
FEEDBACK_WRONG = color565(255, 140, 0)   
FEEDBACK_BAD = color565(220, 40, 40)     
TITLE = color565(40, 40, 50)            
SUCCESS_GOLD = color565(230, 170, 0)    

FONT_5X7 = {
    " ": (0, 0, 0, 0, 0, 0, 0),
    "3": (14, 17, 1, 6, 1, 17, 14),
    "=": (0, 0, 31, 0, 31, 0, 0),
    "M": (17, 27, 21, 17, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "V": (17, 17, 17, 17, 10, 10, 4),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "S": (14, 17, 16, 14, 1, 17, 14),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "A": (4, 10, 17, 17, 31, 17, 17),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "R": (30, 17, 17, 30, 18, 17, 17),
    "s": (14, 16, 14, 1, 14, 0, 0),
    "m": (0, 0, 26, 21, 21, 17, 17),
    "o": (0, 14, 17, 17, 17, 14, 0),
    "d": (1, 1, 15, 17, 17, 15, 0),
    "e": (0, 14, 17, 31, 16, 14, 0),
    "j": (2, 0, 2, 2, 2, 18, 12),
    "u": (0, 17, 17, 17, 17, 15, 0),
    "p": (0, 30, 17, 30, 16, 16, 16),
    "r": (0, 18, 28, 16, 16, 16, 0),
    "i": (0, 4, 0, 4, 4, 4, 14),
    "t": (4, 31, 4, 4, 4, 4, 2),
    "a": (0, 14, 1, 15, 17, 17, 15),
    "n": (0, 0, 22, 25, 17, 17, 17),
    "v": (17, 17, 17, 17, 10, 10, 4),
    "0": (14, 17, 17, 17, 17, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 2, 4, 8, 31),
    "4": (10, 10, 10, 31, 2, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (14, 17, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 4, 4, 4),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 17, 14),
    "C": (14, 16, 16, 16, 16, 16, 14),
    "!": (4, 4, 4, 4, 4, 0, 4),
}


def _draw_text(tft, x, y, s, color, scale=1):
    cw, ch = 6, 7
    for i, c in enumerate(s):
        rows = FONT_5X7.get(c, FONT_5X7[" "])
        cx = x + i * (cw * scale)
        for row in range(min(7, len(rows))):
            bits = rows[row]
            for col in range(5):
                if (bits >> (4 - col)) & 1:
                    tft.fill_rect(cx + (1 + col) * scale, y + row * scale, scale, scale, color)


def draw_background(tft):
    tft.fill(INDIGO_BG)


def draw_pillars(tft, step_done):
    w, h = 32, 22
    gap = 6
    y = 6
    for i in range(3):
        x = 8 + i * (w + gap)
        color = PILLAR_ON if i < step_done else PILLAR_OFF
        tft.fill_rect(x, y, w, h, color)


def draw_door(tft, open_):
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


def draw_vies_restantes(tft, attempts_left):
    y = 138
    tft.fill_rect(4, y - 4, 120, 20, INDIGO_BG)
    s = "vies restantes = " + str(attempts_left)
    _draw_text(tft, 4, y, s, TITLE)


def draw_guess_slots(tft, guess, type_colors, pool_count):
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
    if fb == 2:
        return FEEDBACK_GOOD
    if fb == 1:
        return FEEDBACK_WRONG
    return FEEDBACK_BAD


HISTORY_LEFT_ROWS = 5
HISTORY_RIGHT_ROWS = 5

def _draw_history_column(tft, rows, type_colors, x_start, y_start, row_h, row_margin, box_size, box_gap, dot):
    for row_idx, (g, feedback_peg) in enumerate(rows):
        y = y_start + row_idx * (row_h + row_margin)
        for i in range(4):
            x = x_start + i * (box_size + box_gap)
            
            tft.fill_rect(x - 1, y - 1, box_size + 2, row_h + 2, color565(0, 0, 0))
            
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
    dot_size = 8
    y = 118
    x_start = 28
    gap = 6
    for i in range(4):
        x = x_start + i * (dot_size + gap)
        fb = feedback_peg[i] if i < len(feedback_peg) else 0
        tft.fill_rect(x, y, dot_size, dot_size, _feedback_color(fb))


def draw_step_indicator(tft, step, total, attempts_left):
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
    draw_background(tft)
    draw_pillars(tft, step - 1)  
    draw_guess_slots(tft, guess, type_colors, pool_count)
    if history:
        draw_history(tft, history, type_colors)
    draw_feedback(tft, feedback_peg)
    draw_vies_restantes(tft, attempts_left)


def draw_success_screen(tft):
    draw_background(tft)
    draw_pillars(tft, 3)
    draw_door(tft, True)
    _draw_text(tft, 4, 76, "VICTOIRE !", SUCCESS_GOLD, scale=2)


def draw_visual_mode(tft, frame, type_colors):
    tft.fill(INDIGO_BG)
    _draw_text(tft, 4, 62, "MODE VISUALISATION", TITLE)
    _draw_text(tft, 4, 72, "3 s = mode jeu", TITLE)


def draw_visual_mode_door_open(tft, type_colors):
    tft.fill(INDIGO_BG)
    _draw_text(tft, 4, 62, "MODE VISUALISATION", TITLE)
    _draw_text(tft, 4, 72, "porte ouverte", TITLE)


def draw_idle_screen(tft, step, total, attempts_left=10):
    draw_background(tft)
    draw_pillars(tft, 0)
    draw_guess_slots(tft, [None, None, None, None], [], 0)
    draw_feedback(tft, [0, 0, 0, 0])
    draw_vies_restantes(tft, attempts_left)


