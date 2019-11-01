#!/usr/bin/env python3

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

coinsValue: float = 0.00
coinInserted: bool = False

GPIO.add_event_detect(4, GPIO.RISING)

def coin_added(value):
    global coinInserted
    global coinsValue
    coinsValue = coinsValue + 50
    coinInserted = True
    print(value)

GPIO.add_event_callback(4, coin_added)

while True:
    if coinInserted:
        coinInserted = False
        print("Coin inserted. New credit: {0:.2f}€".format(coinsValue / 100))
