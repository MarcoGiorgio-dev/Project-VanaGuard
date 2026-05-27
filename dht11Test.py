import RPi.GPIO as GPIO
import dht11
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

print("Tester DHT11 sensor — tryk Ctrl+C for at stoppe.\n")

try:
    while True:
        dhtData = dht11.DHT11(pin=6)
        humTemp = dhtData.read()
        if humTemp.is_valid():
            print(f"Temperatur: {humTemp.temperature}°C  |  Fugtighed: {humTemp.humidity}%")
        else:
            print("Aflæsning fejlede, prøver igen...")
        sleep(1)
except KeyboardInterrupt:
    print("\nTest stoppet.")
finally:
    GPIO.cleanup()
