from ili9341 import color565


INDIGO_BG = color565(236, 245, 255)
PANEL_TOP = color565(210, 228, 255)
PANEL_BOTTOM = color565(246, 250, 255)
POKE_RED = color565(233, 67, 82)
POKE_WHITE = color565(255, 255, 255)
POKE_DARK = color565(38, 44, 64)
PILLAR_OFF = color565(170, 190, 225)
PILLAR_ON = color565(255, 210, 60)
DOOR = color565(63, 82, 140)
DOOR_LINE = color565(36, 50, 94)
SLOT_BORDER = color565(42, 78, 154)
SLOT_EMPTY = color565(255, 255, 255)
FEEDBACK_GOOD = color565(46, 178, 90)
FEEDBACK_WRONG = color565(255, 140, 45)
FEEDBACK_BAD = color565(225, 56, 72)
TITLE = color565(28, 48, 96)
TEXT_SUB = color565(76, 102, 168)
TEXT_ON_DARK = color565(255, 255, 255)
SUCCESS_GOLD = color565(255, 214, 80)
BASE_W = 128
BASE_H = 160


class _ScaledCanvas:
    def __init__(self, tft):
        self._tft = tft
        w = getattr(tft, "width", BASE_W)
        h = getattr(tft, "height", BASE_H)
        self._scale = min(w / BASE_W, h / BASE_H)
        if self._scale <= 0:
            self._scale = 1.0
        self._ox = int((w - BASE_W * self._scale) // 2)
        self._oy = int((h - BASE_H * self._scale) // 2)

    def _sx(self, x):
        return int(round(self._ox + x * self._scale))

    def _sy(self, y):
        return int(round(self._oy + y * self._scale))

    def _sw(self, w):
        # Derive width from transformed bounds to avoid rounding drift.
        return max(1, self._sx(w) - self._sx(0))

    def _sh(self, h):
        # Same strategy vertically for consistent glyph height.
        return max(1, self._sy(h) - self._sy(0))

    def fill(self, color):
        self._tft.fill(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = self._sx(x)
        y0 = self._sy(y)
        x1 = self._sx(x + w)
        y1 = self._sy(y + h)
        self._tft.fill_rect(x0, y0, max(1, x1 - x0), max(1, y1 - y0), color)


def _canvas(tft):
    if isinstance(tft, _ScaledCanvas):
        return tft
    return _ScaledCanvas(tft)

FONT_W = 3
FONT_H = 5

FONT = {
    " ": (0, 0, 0, 0, 0),
    "A": (2, 5, 7, 5, 5),
    "B": (6, 5, 6, 5, 6),
    "C": (3, 4, 4, 4, 3),
    "D": (6, 5, 5, 5, 6),
    "E": (7, 4, 7, 4, 7),
    "F": (7, 4, 6, 4, 4),
    "G": (7, 4, 5, 5, 7),
    "H": (5, 5, 7, 5, 5),
    "I": (7, 2, 2, 2, 7),
    "J": (3, 1, 1, 5, 2),
    "K": (5, 5, 6, 5, 5),
    "L": (4, 4, 4, 4, 7),
    "M": (5, 7, 5, 5, 5),
    "N": (6, 5, 5, 5, 5),
    "O": (2, 5, 5, 5, 2),
    "P": (6, 5, 6, 4, 4),
    "Q": (2, 5, 5, 2, 1),
    "R": (6, 5, 6, 5, 5),
    "S": (3, 4, 2, 1, 6),
    "T": (7, 2, 2, 2, 2),
    "U": (5, 5, 5, 5, 7),
    "V": (5, 5, 5, 2, 2),
    "W": (5, 5, 7, 7, 5),
    "X": (5, 5, 2, 5, 5),
    "Y": (5, 5, 2, 2, 2),
    "Z": (7, 1, 2, 4, 7),
    "0": (7, 5, 5, 5, 7),
    "1": (2, 6, 2, 2, 7),
    "2": (6, 1, 2, 4, 7),
    "3": (7, 1, 3, 1, 7),
    "4": (5, 5, 7, 1, 1),
    "5": (7, 4, 7, 1, 7),
    "6": (7, 4, 7, 5, 7),
    "7": (7, 1, 2, 2, 2),
    "8": (7, 5, 7, 5, 7),
    "9": (7, 5, 7, 1, 7),
    "!": (2, 2, 2, 0, 2),
    ":": (0, 2, 0, 2, 0),
    "/": (1, 1, 2, 4, 4),
    "-": (0, 0, 7, 0, 0),
    ".": (0, 0, 0, 0, 2),
    "=": (0, 7, 0, 7, 0),
    "?": (6, 1, 2, 0, 2),
}


def _draw_glyph_runs(tft, x, y, rows, color, scale):
    for row in range(min(FONT_H, len(rows))):
        bits = rows[row]
        run_start = -1
        for col in range(FONT_W):
            bit_on = (bits >> (FONT_W - 1 - col)) & 1
            if bit_on and run_start < 0:
                run_start = col
            at_row_end = (col == FONT_W - 1)
            if run_start >= 0 and ((not bit_on) or at_row_end):
                run_end = col if bit_on and at_row_end else col - 1
                run_w = (run_end - run_start + 1) * scale
                rx = x + run_start * scale
                ry = y + row * scale
                tft.fill_rect(rx, ry, run_w, scale, color)
                run_start = -1


def _draw_text(tft, x, y, s, color, scale=1):
    cw = FONT_W + 1
    for i, c in enumerate(s):
        ch = c.upper() if c.islower() else c
        rows = FONT.get(ch, FONT[" "])
        cx = x + i * (cw * scale)
        _draw_glyph_runs(tft, cx, y, rows, color, scale)


def draw_background(tft):
    tft.fill(INDIGO_BG)
    tft.fill_rect(0, 0, 128, 28, PANEL_TOP)
    tft.fill_rect(0, 28, 128, 94, PANEL_BOTTOM)
    tft.fill_rect(0, 130, 128, 30, color565(228, 238, 255))
    tft.fill_rect(0, 27, 128, 1, POKE_DARK)
    tft.fill_rect(0, 129, 128, 1, POKE_DARK)


def _draw_pokeball_icon(tft, x, y):
    tft.fill_rect(x, y, 14, 6, POKE_RED)
    tft.fill_rect(x, y + 6, 14, 6, POKE_WHITE)
    tft.fill_rect(x, y + 5, 14, 2, POKE_DARK)
    tft.fill_rect(x + 5, y + 4, 4, 4, POKE_WHITE)
    tft.fill_rect(x + 6, y + 5, 2, 2, POKE_DARK)


def _draw_header(tft, title, subtitle=None):
    _draw_pokeball_icon(tft, 108, 7)
    _draw_text(tft, 4, 6, title, TITLE)
    if subtitle:
        _draw_text(tft, 4, 15, subtitle, TEXT_SUB)


def draw_pillars(tft, step_done):
    w, h = 20, 10
    gap = 6
    y = 44
    for i in range(3):
        x = 36 + i * (w + gap)
        color = PILLAR_ON if i < step_done else PILLAR_OFF
        tft.fill_rect(x, y, w, h, color)
        _draw_text(tft, x + 7, y + 1, str(i + 1), POKE_DARK)


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
    y = 150
    tft.fill_rect(4, y - 3, 120, 12, color565(214, 228, 255))
    s = "vies restantes: " + str(attempts_left)
    _draw_text(tft, 8, y, s, TITLE)


def draw_guess_slots(tft, guess, type_colors, pool_count):
    slot_size = 22
    gap = 6
    y = 68
    for i in range(4):
        x = 6 + i * (slot_size + gap)
        tft.fill_rect(x - 2, y - 2, slot_size + 4, slot_size + 4, SLOT_BORDER)
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
            
            tft.fill_rect(x - 1, y - 1, box_size + 2, row_h + 2, color565(42, 78, 154))
            
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
    row_h = 4
    row_margin = 3
    box_size = 6
    box_gap = 1
    dot = 4
    y_start = 103
    last_6 = history[-6:]
    left_rows = last_6[:3]
    right_rows = last_6[3:]
    col_width = 4 * (box_size + box_gap) + box_gap + 4 * (dot + 1)
    x_left = 4
    x_right = 128 - 4 - col_width
    _draw_history_column(tft, left_rows, type_colors, x_left, y_start, row_h, row_margin, box_size, box_gap, dot)
    _draw_history_column(tft, right_rows, type_colors, x_right, y_start, row_h, row_margin, box_size, box_gap, dot)


def draw_feedback(tft, feedback_peg):
    dot_size = 6
    y = 140
    x_start = 28
    gap = 6
    for i in range(4):
        x = x_start + i * (dot_size + gap)
        fb = feedback_peg[i] if i < len(feedback_peg) else 0
        tft.fill_rect(x - 1, y - 1, dot_size + 2, dot_size + 2, color565(255, 255, 255))
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
    tft = _canvas(tft)
    draw_background(tft)
    _draw_header(tft, "POKE LAB", "etape " + str(step) + "/" + str(total))
    _draw_text(tft, 4, 32, "badges", TEXT_SUB)
    draw_pillars(tft, step - 1)
    _draw_text(tft, 4, 57, "sequence", TEXT_SUB)
    draw_guess_slots(tft, guess, type_colors, pool_count)
    if history:
        _draw_text(tft, 4, 96, "historique", TEXT_SUB)
        draw_history(tft, history, type_colors)
    _draw_text(tft, 4, 132, "indices", TEXT_SUB)
    draw_feedback(tft, feedback_peg)
    draw_vies_restantes(tft, attempts_left)


def draw_success_screen(tft):
    tft = _canvas(tft)
    draw_background(tft)
    _draw_header(tft, "POKE LAB", "COFFRE DEVERROUILLE")
    _draw_text(tft, 4, 32, "BADGES", TEXT_SUB)
    draw_pillars(tft, 3)
    _draw_text(tft, 14, 70, "VICTOIRE !", SUCCESS_GOLD, scale=2)
    _draw_text(tft, 28, 105, "BADGE GAGNE", TITLE, scale=1.5)


def draw_visual_mode(tft, frame, type_colors):
    tft = _canvas(tft)
    draw_background(tft)
    _draw_header(tft, "POKE LAB", "mode visualisation")
    _draw_text(tft, 4, 65, "MAINTENIR 3 S", TITLE, scale=1.5)
    _draw_text(tft, 4, 85, "POUR OUVRIR", TITLE, scale=1.5)
    _draw_text(tft, 4, 105, "PORTE", TITLE, scale=1.5)


def draw_visual_mode_door_open(tft, type_colors):
    tft = _canvas(tft)
    draw_background(tft)
    _draw_header(tft, "POKE LAB", "mode visualisation")
    _draw_text(tft, 4, 65, "PORTE OUVERTE", FEEDBACK_GOOD, scale=1.5)
    _draw_text(tft, 4, 90, "MAINTENIR POUR", TITLE, scale=1.5)
    _draw_text(tft, 4, 110, "FERMER", TITLE, scale=1.5)


def draw_idle_screen(tft, step, total, attempts_left=8):
    tft = _canvas(tft)
    draw_background(tft)
    _draw_header(tft, "POKE LAB", "choisis un type")
    _draw_text(tft, 4, 32, "badges", TEXT_SUB)
    draw_pillars(tft, 0)
    _draw_text(tft, 4, 57, "sequence", TEXT_SUB)
    draw_guess_slots(tft, [None, None, None, None], [], 0)
    _draw_text(tft, 4, 132, "indices", TEXT_SUB)
    draw_feedback(tft, [0, 0, 0, 0])
    _draw_text(tft, 4, 98, "appuie pour lancer", TITLE)
    draw_vies_restantes(tft, attempts_left)


