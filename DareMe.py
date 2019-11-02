#!/usr/bin/env python3
from challenge import ChallengeStack
from DareFormatter import Dare
from os.path import expanduser
import RPi.GPIO as GPIO
from thermalprinter import *

coin_pin = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(coin_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

coinsValue: float = 0.00
coinInserted: bool = False

GPIO.add_event_detect(coin_pin, GPIO.RISING)


def coin_added(value):
    global coinInserted
    global coinsValue
    coinsValue = coinsValue + 50
    coinInserted = True
    print(value)


GPIO.add_event_callback(coin_pin, coin_added)

home = expanduser("~")
cf = home + "/challenges"
stack = ChallengeStack.from_folder(cf)
print(stack)
d = Dare.from_file(home + "/dare.txt")

with ThermalPrinter(port='/dev/serial0') as printer:
    while True:
        if coinInserted:
            coinInserted = False
            print("Coin inserted. New credit: {0:.2f}€".format(coinsValue / 100))
            msg = d.compile(stack.pick(), stack.passed)
            print(msg)
            printer.out(msg, strike=True)
            printer.feed(2)
