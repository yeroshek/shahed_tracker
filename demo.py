from gpiozero import Device, PWMOutputDevice, DigitalInputDevice, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

Device.pin_factory = PiGPIOFactory()

servoHorizontal = Servo(14, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servoVertical = Servo(15, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)


buttonOut = PWMOutputDevice(16)
buttonIn = DigitalInputDevice(20)

# Включаем лампочку на кнопке, чтобы показать что программа запущена
buttonOut.on()


while True:
    if (buttonIn.value == 0):
        continue

    servoHorizontal.value = 0.2
    servoVertical.max()
    sleep(2)
    
    if (buttonIn.value == 0):
        continue
    
    servoHorizontal.value = 0
    servoVertical.mid()
    sleep(1)
    
    if (buttonIn.value == 0):
        continue

    servoHorizontal.value = -0.2
    servoVertical.min()
    sleep(2)
    
    if (buttonIn.value == 0):
        continue

    servoHorizontal.value = 0
    servoVertical.mid()
    sleep(1)

