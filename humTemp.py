import RPi.GPIO as GPIO
import dht11
from time import sleep
import threading

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

_hum = None
_temp = None
_lock = threading.Lock()

dhtData = dht11.DHT11(pin=6)

def _read_loop():
    global _hum, _temp
    while True:
        for _ in range(5):
            reading = dhtData.read()
            if reading.is_valid():
                with _lock:
                    _hum = reading.humidity
                    _temp = reading.temperature
                print(f"Temperatur: {_temp}  Fugtighed: {_hum}")
                break
            sleep(0.5)
        sleep(10)

_thread = threading.Thread(target=_read_loop, daemon=True)
_thread.start()

def get_humTemp():
    with _lock:
        return _hum, _temp
