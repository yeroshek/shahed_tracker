#!/usr/bin/python3
from gpiozero import Device, PWMOutputDevice, DigitalInputDevice, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

Device.pin_factory = PiGPIOFactory()

laser = PWMOutputDevice(23)

servoHorizontal = Servo(18, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

servoHorizontal.value = 0

# Включаем лампочку на кнопке, чтобы показать что программа запущена
laser.off()

# sleep(1)

# laser.off()