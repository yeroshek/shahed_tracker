from gpiozero import Device, PWMOutputDevice, DigitalInputDevice, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

SLEEP_HORIZONTAL_TIME = 0.45
HORIZONTAL_SPEED = 0.1

VERTICAL_MIN = -0.85
VERTICAL_MAX = 0.85
SLEEP_VERTICAL_TIME = 2
VERTICAL_STEPS = 50

Device.pin_factory = PiGPIOFactory()

servoHorizontal = Servo(14, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servoVertical = Servo(15, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

servoHorizontal.value = 0
servoVertical.value = VERTICAL_MIN


def rotate_horizontal(steps):
    sign = -1 if steps < 0 else 1
    servoHorizontal.value = sign * HORIZONTAL_SPEED
    sleep(abs(steps) * SLEEP_HORIZONTAL_TIME)
    servoHorizontal.value = 0

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
    for _ in range(6):
        scan_vertical()
        rotate_horizontal(1)
    
    rotate_horizontal(-7)

try:
    while True:
        scan_air()
    
except KeyboardInterrupt:
    servoHorizontal.value = 0
except Exception as e:
    servoHorizontal.value = 0
