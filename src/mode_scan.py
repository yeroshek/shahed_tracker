from gpiozero import Device, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

SLEEP_HORIZONTAL_TIME = 0.5
HORIZONTAL_STEPS = 6

VERTICAL_MIN = -0.85
VERTICAL_MAX = 0
SLEEP_VERTICAL_TIME = 2
VERTICAL_STEPS = 60

Device.pin_factory = PiGPIOFactory()

servoHorizontal = Servo(18, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servoVertical = Servo(15, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)


def rotate_horizontal(value):
    servoHorizontal.value = value
    sleep(SLEEP_HORIZONTAL_TIME)

def smooth_transition(start, end, steps):
    step_value = (end - start) / (steps - 1)
    return [start + i * step_value for i in range(steps)]

def scan_vertical():
    current_value = servoVertical.value
    target_value = VERTICAL_MAX if current_value == VERTICAL_MIN else VERTICAL_MIN
    for value in smooth_transition(current_value, target_value, VERTICAL_STEPS):
        servoVertical.value = value
        sleep(SLEEP_VERTICAL_TIME / VERTICAL_STEPS)

def scan_air():
    for horizontalValue in smooth_transition(-1, 1, HORIZONTAL_STEPS):
        rotate_horizontal(horizontalValue)
        scan_vertical()

    rotate_horizontal(-1)

def start_scan(mode):
    servoHorizontal.value = -1
    servoVertical.value = VERTICAL_MIN

    sleep(SLEEP_HORIZONTAL_TIME)

    while True:
        if mode.value == 'SCAN':
            scan_air()
        else:
            sleep(0.25)
