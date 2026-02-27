from machine import Pin, PWM

PIN_FILAMENT = 13

filament = PWM(Pin(PIN_FILAMENT))
filament.freq(1000)

_duty = 0
_up = True

_MIN_DUTY = 0
_MAX_DUTY = 65535
_STEP = 1000


def update_filament():
    global _duty, _up

    if _up:
        _duty += _STEP
        if _duty >= _MAX_DUTY:
            _duty = _MAX_DUTY
            _up = False
    else:
        _duty -= _STEP
        if _duty <= _MIN_DUTY:
            _duty = _MIN_DUTY
            _up = True

    filament.duty_u16(_duty)


def filament_off():
    global _duty, _up
    _duty = 0
    _up = True
    filament.duty_u16(0)


def set_filament_percent(percent):
    global _duty, _up
    if percent < 0:
        percent = 0
    if percent > 100:
        percent = 100
    _up = False
    span = _MAX_DUTY - _MIN_DUTY
    _duty = int(_MIN_DUTY + (percent / 100.0) * span)
    filament.duty_u16(_duty)

