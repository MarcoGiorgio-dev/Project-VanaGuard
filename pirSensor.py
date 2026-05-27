import RPi.GPIO as GPIO
import time

pir_pin = 27

def pir_setup():
 GPIO.setup(pir_pin, GPIO.IN)  
 print("PIR Sensor klar! Afventer bevægelse.")

def read_pir():
    if GPIO.input(pir_pin):
        print("Bevægelse registreret!")
        return True
    else:
        return False
 
GPIO.setmode(GPIO.BCM) 
