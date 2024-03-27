
from gpiozero import Device, PWMOutputDevice, DigitalInputDevice, Servo
from gpiozero.pins.pigpio import PiGPIOFactory

Device.pin_factory = PiGPIOFactory()

servoHorizontal = Servo(15, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)


servoHorizontal.value = 0
