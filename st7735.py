from machine import Pin
import time

class ST7735:
    def __init__(self, spi, cs, dc, rst, width=128, height=160):
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT, value=1)
        self.dc = Pin(dc, Pin.OUT, value=0)
        self.rst = Pin(rst, Pin.OUT, value=1)
        self.width = width
        self.height = height

        self.reset()
        self._init_display()

    def reset(self):
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(150)

    def write_cmd(self, cmd):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)

    def write_data(self, data):
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(data)
        self.cs.value(1)

    def _init_display(self):
        self.write_cmd(0x01)
        time.sleep_ms(150)

        self.write_cmd(0x11)    
        time.sleep_ms(150)

        self.write_cmd(0x3A)
        self.write_data(bytearray([0x05]))

        self.write_cmd(0x29)
        time.sleep_ms(50)

    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A)
        self.write_data(bytearray([0, x0, 0, x1]))
        self.write_cmd(0x2B)
        self.write_data(bytearray([0, y0, 0, y1]))
        self.write_cmd(0x2C)

    def fill(self, color):
        self.set_window(0, 0, self.width - 1, self.height - 1)
        hi = color >> 8
        lo = color & 0xFF
        self.dc.value(1)
        self.cs.value(0)
        for _ in range(self.width * self.height):
            self.spi.write(bytearray([hi, lo]))
        self.cs.value(1)

    def fill_rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        x1 = min(x + w - 1, self.width - 1)
        y1 = min(y + h - 1, self.height - 1)
        x = max(0, x)
        y = max(0, y)
        w = x1 - x + 1
        h = y1 - y + 1
        self.set_window(x, y, x1, y1)
        hi = color >> 8
        lo = color & 0xFF
        self.dc.value(1)
        self.cs.value(0)
        for _ in range(w * h):
            self.spi.write(bytearray([hi, lo]))
        self.cs.value(1)


def color565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)