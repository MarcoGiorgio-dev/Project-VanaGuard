import RPi.GPIO as GPIO
import dht11
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

dhtData = dht11.DHT11(pin=6)

def get_humTemp():
    for _ in range(5):
        humTemp = dhtData.read()
        if humTemp.is_valid():
            print("Temperatur: ", humTemp.temperature)
            print("Fugtighed: ", humTemp.humidity)
            return humTemp.humidity, humTemp.temperature
        sleep(0.5)
    print("Input fra DHT11 ikke valideret, prøver igen senere.")
    return None, None
