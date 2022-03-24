import bme680
import time
import logging
import RPi.GPIO as GPIO
import os
from gpiozero import LED


from pyfirmata import Arduino, util
from time import sleep
board = Arduino('/dev/ttyACM0') # Change to your port


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO_PIN = 4
GPIO.setup(GPIO_PIN, GPIO.OUT)
motor = LED(17)
GPFrequency = 50
pwm = GPIO.PWM(GPIO_PIN, GPFrequency)
successSound = "aplay /home/pi/Desktop/Face_Recog/Success.wav"
tempWarning =  "aplay /home/pi/Desktop/tempWarning.wav"
lightOn = "aplay /home/pi/Desktop/Project Audio WAV_lightsOn.wav"
lightOff = "aplay /home/pi/Desktop/Project Audio WAV_lightsOff.wav"


cooling = bool(False)
idleFan = bool(False)

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


print('\n\nTemprature: ')


reader = util.Iterator(board)
reader.start()
light_sensor = board.get_pin("a:0:i")



try:
    logging.basicConfig(filename='/home/pi/Desktop/BME680/temp.log',level=logging.DEBUG)
    logging.info("Program Started")
    while True:
        
        
        
        
      
        if light_sensor.read():
            light_level = light_sensor.read()
            if light_level < 0.4:
               board.digital[12].write(1)
            else:
                board.digital[12].write(0)
           
        
           
           
           
        
        if sensor.get_sensor_data():
            degrees_c = sensor.data.temperature
            degrees_f = (sensor.data.temperature * 9/5) + 32
            idleFan = bool(True)
            if degrees_c >= 25:
                if idleFan != cooling:
                
                    logging.warning("Temperature is "+format(degrees_c) + " in degrees C and "+ format(degrees_f) + " in fahrenheit THIS IS TOO HOT")
                    #pwm.start(50)
                    os.system(tempWarning)
                    print('Check')
                    board.digital[3].write(1)
                    cooling = bool(True)
                    #pwm.stop()
                
            else:
                logging.info("Temperature is fine it is currently " + format(degrees_c)  + " Temperature in farenheight is: " + format(degrees_f))
                board.digital[3].write(0)
                print('else')
                cooling = bool(False)
                
                       
            

except KeyboardInterrupt:
    logging.info("Program Terminated")
    GPIO.cleanup()
    pass
