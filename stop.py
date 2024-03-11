from gpiozero import Device, PWMOutputDevice, DigitalInputDevice, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

Device.pin_factory = PiGPIOFactory()

servoHorizontal = Servo(14, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servoVertical = Servo(15, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

servoHorizontal.value = 0
servoVertical.value = -1