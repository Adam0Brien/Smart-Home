from gpiozero import Servo     # Imports for servo movement
from gpiozero.pins.pigpio import PiGPIOFactory
factory = PiGPIOFactory()

from time import sleep 
servo = Servo(12 , pin_factory=factory)

while True:
    servo.min()
    sleep(2)
    servo.max()
    sleep(1)