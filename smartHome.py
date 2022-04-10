import bme680
import time
import requests
import logging
import RPi.GPIO as GPIO
import os
from gpiozero import LED
from pyfirmata import Arduino, util
from time import sleep
from gpiozero import MotionSensor
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo   


factory = PiGPIOFactory()
servo = Servo(12 , pin_factory=factory)
pir = MotionSensor(27)
board = Arduino('/dev/ttyACM0') # Change to your port


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO_PIN = 4
GPIO.setup(GPIO_PIN, GPIO.OUT)
motor = LED(17)

lightURL =    'https://api.thingspeak.com/update?api_key=08KLEMNHHRDEECV9&field2='
tempURL = 'https://api.thingspeak.com/update?api_key=08KLEMNHHRDEECV9&field1='
doorURL = 'https://api.thingspeak.com/update?api_key=08KLEMNHHRDEECV9&field3='


successSoundWAV = "aplay /home/pi/Desktop/Face_Recog/Success.wav"
tempWarningWAV =  "aplay /home/pi/Desktop/tempWarning.wav"
lightOnWAV = "aplay /home/pi/Desktop/lightsOn.wav"
openDoorWAV = "aplay /home/pi/Desktop/openDoor.wav"


cooling = bool(False)
idleFan = bool(False)

openDoor = bool(False)
idleDoor = bool(False)

lightOn = bool(False)
idleLight = bool(False)

print("Starting.....")

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except (RuntimeError, IOError):
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)


sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)


reader = util.Iterator(board)
reader.start()
light_sensor = board.get_pin("a:0:i")



try:
    logging.basicConfig(filename='/home/pi/Desktop/smartHome.log',level=logging.INFO)
    logging.info("Program Started")
    while True:
        
        #lighting system logic
        if light_sensor.read():
            light_level = light_sensor.read()
            idleLight = bool(True)
            if light_level <= 0.4:
                if idleLight != lightOn:
                       os.system(lightOnWAV)
                       board.digital[2].write(1)
                       URL = lightURL + str(light_level)
                       response = requests.get(url = URL)
                       logging.info("Light has been Turned On")
                       lightOn = bool(True)
                                
            else:
                    
                board.digital[2].write(0)
                URL = lightURL + str(light_level)
                response = requests.get(url = URL)
                #print("Light: "+response.text)
                logging.info("Light has been Turned Off")
                lightOn = bool(False)
               
        
           
           
           
        #cooling system logic
        if sensor.get_sensor_data():
            degrees_c = sensor.data.temperature
            degrees_f = (sensor.data.temperature * 9/5) + 32
            idleFan = bool(True)
            if degrees_c >= 25:
                if idleFan != cooling:
                
                    logging.warning("Temperature is "+format(degrees_c) + " in degrees C and "+ format(degrees_f) + " in fahrenheit THIS IS TOO HOT")
                    os.system(tempWarningWAV)
                    board.digital[3].write(1)
                    cooling = bool(True)
                    URL = tempURL + str(degrees_c)
                    response = requests.get(url = URL)
                    #print("Temp: " + response.text)
                    
                
            else:
                logging.info("Temperature is fine it is currently " + format(degrees_c)  + " Temperature in farenheight is: " + format(degrees_f))
                board.digital[3].write(0)
                cooling = bool(False)
                URL = tempURL + str(degrees_c)
                response = requests.get(url = URL)
                
                       
                       
    
        #door opening logic (Had Open CV working with face ID check website for reference)
        idleDoor = bool(True)
        if(pir.value == 1):
            if idleDoor != openDoor:

                logging.warning("Motion Detected")
                os.system(openDoorWAV)
                servo.min()
                URL = doorURL + str(pir.value)
                response = requests.get(url = URL)
                openDoor = bool(True)
            
        elif(pir.value == 0):
            servo.max()
            openDoor = bool(False)
            URL = doorURL + str(pir.value)
            response = requests.get(url = URL)
    
    
    
except KeyboardInterrupt:
    logging.info("Program Terminated")
    GPIO.cleanup()
    pass

