from machine import Pin
import time

# Commandes ILI9341
_SWRESET  = 0x01
_SLPOUT   = 0x11
_DISPON   = 0x29
_CASET    = 0x2A
_RASET    = 0x2B
_RAMWR    = 0x2C
_MADCTL   = 0x36
_COLMOD   = 0x3A

# Orientation / rotation
_MADCTL_MX = 0x40
_MADCTL_MY = 0x80
_MADCTL_MV = 0x20
_MADCTL_RGB= 0x00

# Couleur RGB → 16-bit
def color565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

class ILI9341:
    def __init__(self, spi, cs, dc, rst, width=240, height=320):
        self.spi = spi
        self.cs = None if cs is None else (cs if isinstance(cs, Pin) else Pin(cs))
        self.dc = dc if isinstance(dc, Pin) else Pin(dc)
        self.rst = rst if isinstance(rst, Pin) else Pin(rst)

        if self.cs:
            self.cs.init(Pin.OUT, value=1)
        self.dc.init(Pin.OUT, value=0)
        self.rst.init(Pin.OUT, value=1)

        self.width = width
        self.height = height

        self.init_display()

    # Commande et Data SPI
    def write_cmd(self, cmd):
        self.dc.value(0)
        if self.cs:
            self.cs.value(0)
        self.spi.write(bytearray([cmd]))
        if self.cs:
            self.cs.value(1)

    def write_data(self, data):
        self.dc.value(1)
        if self.cs:
            self.cs.value(0)
        self.spi.write(data)
        if self.cs:
            self.cs.value(1)

    # Reset matériel
    def hardware_reset(self):
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(120)

    # Initialisation écran
    def init_display(self):
        self.hardware_reset()

        self.write_cmd(_SWRESET)
        time.sleep_ms(150)

        self.write_cmd(_SLPOUT)
        time.sleep_ms(120)

        self.write_cmd(_COLMOD)
        self.write_data(bytearray([0x55]))  # RGB565

        self.write_cmd(_MADCTL)
        self.write_data(bytearray([_MADCTL_MX | _MADCTL_RGB]))

        self.write_cmd(_DISPON)
        time.sleep_ms(100)

    # Définir la fenêtre d’écriture
    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(_CASET)
        self.write_data(bytearray([
            (x0 >> 8) & 0xFF, x0 & 0xFF,
            (x1 >> 8) & 0xFF, x1 & 0xFF
        ]))

        self.write_cmd(_RASET)
        self.write_data(bytearray([
            (y0 >> 8) & 0xFF, y0 & 0xFF,
            (y1 >> 8) & 0xFF, y1 & 0xFF
        ]))

        self.write_cmd(_RAMWR)

    # Remplir l’écran entier
    def fill(self, color):
        self.set_window(0, 0, self.width - 1, self.height - 1)
        hi = color >> 8
        lo = color & 0xFF
        line = bytearray([hi, lo] * self.width)
        for _ in range(self.height):
            self.write_data(line)

    # Rectangle rempli
    def fill_rect(self, x, y, w, h, color):
        self.set_window(x, y, x + w - 1, y + h - 1)
        hi = color >> 8
        lo = color & 0xFF
        line = bytearray([hi, lo] * w)
        for _ in range(h):
            self.write_data(line)

    # Pixel unique
    def pixel(self, x, y, color):
        self.set_window(x, y, x, y)
        self.write_data(bytearray([color >> 8, color & 0xFF]))

    # Texte simple 8x8 ASCII, pas de framebuf
    def text(self, x, y, string, color):
        for i, c in enumerate(string):
            cx = x + i * 8
            cy = y
            self.draw_char(cx, cy, c, color)

    # Dessin d’un caractère 8x8 basique
    def draw_char(self, x, y, char, color):
        # Font minimaliste 8x8, ASCII 32..127
        font = [
            0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00, # espace
            # Ajouter les caractères si nécessaire
        ]
        # Pour l’instant on simule le caractère par un rectangle
        self.fill_rect(x, y, 6, 8, color)
