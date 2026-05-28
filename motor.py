import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

class Stepper:
    def __init__(self, pins, delay=0.002):
        self.pins = pins
        self.delay = delay

        for p in pins:
            GPIO.setup(p, GPIO.OUT)
            GPIO.output(p, 0)
            
        self.sequence = [
            [1,0,0,0],
            [1,1,0,0],
            [0,1,0,0],
            [0,1,1,0],
            [0,0,1,0],
            [0,0,1,1],
            [0,0,0,1],
            [1,0,0,1]
        ]
    def step(self, steps, direction=1):
        seq = self.sequence if direction == 1 else self.sequence[::-1]
        for _ in range(steps):
            for pattern in seq:
                for pin, val in zip(self.pins, pattern):
                    GPIO.output(pin, val)
                sleep(self.delay)
    
    def stop(self):
        for p in self.pins:
            GPIO.output(p, 0)

stepper = Stepper(pins=[5, 17, 4, 15])

def fan_setup(fan_pin):
    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.output(fan_pin, 0)

def open_window():
    stepper.step(steps=1200, direction=1)
    stepper.stop()

def close_window():
    stepper.step(steps=1200, direction=-1)
    stepper.stop()

def turn_on_fan(fan_pin):
    GPIO.output(fan_pin, 1)

def turn_off_fan(fan_pin):
    GPIO.output(fan_pin, 0)

def janitor():
    GPIO.cleanup()
