from machine import Pin, SPI
import ili9341
import time

spi = SPI(
    0,
    baudrate=20_000_000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(19),
)

# Mets le vrai pin CS si ton écran l'utilise
tft = ili9341.ILI9341(
    spi,
    cs=Pin(17),      # <- évite None
    dc=Pin(21),
    rst=Pin(20),
)

while True:
    tft.fill(ili9341.color565(255, 0, 0))
    time.sleep(1)
    tft.fill(ili9341.color565(0, 255, 0))
    time.sleep(1)
    tft.fill(ili9341.color565(0, 0, 255))
    time.sleep(1)