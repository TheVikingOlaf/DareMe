#!/usr/bin/env python3
from challenge import ChallengeStack
from DareFormatter import Dare
from os.path import expanduser
import RPi.GPIO as GPIO
from thermalprinter import *
import datetime

coin_pin = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(coin_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

coinsValue: float = 0.00
coinInserted: bool = False

last_timestamp = datetime.datetime.utcnow()
GUARD_INTERVAL_IN_SECONDS = 5

GPIO.add_event_detect(coin_pin, GPIO.RISING)


def guard_interval_passed(timestamp: datetime.datetime) -> bool:
    if timestamp is None:
        return True
    now = datetime.datetime.utcnow()
    delta = now - timestamp
    if int(delta.total_seconds()) >= GUARD_INTERVAL_IN_SECONDS:
        return True
    return False


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
        if coinInserted and guard_interval_passed(last_timestamp):
            print("Coin inserted. New credit: {0:.2f}€".format(coinsValue / 100))
            msg = d.compile(stack.pick(), stack.cur_count)
            print(msg)
            printer.out(msg, justify='C', strike=True)
            printer.feed(2)
            last_timestamp = datetime.datetime.utcnow()
        coinInserted = False
