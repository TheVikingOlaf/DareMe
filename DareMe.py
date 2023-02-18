#!/usr/bin/env python3
import os
from challenge import ChallengeStack
from DareFormatter import Dare
from os.path import expanduser
import RPi.GPIO as GPIO
from thermalprinter import *
import datetime

import logging
from rich.logging import RichHandler

COIN_PIN_NUMBER = 4

coinsValue: float = 0.00
coinInserted: bool = False
GUARD_INTERVAL_IN_SECONDS = 5
ENABLE_PRINTING: bool = True

_logger = logging.getLogger(__name__)


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


def configure_logger() -> None:
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True, markup=True)]
    )


def main() -> None:
    global coinInserted
    global coinsValue
    configure_logger()

    _logger.info("Setting up GPIOs and callbacks")

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(COIN_PIN_NUMBER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(COIN_PIN_NUMBER, GPIO.RISING)
    GPIO.add_event_callback(COIN_PIN_NUMBER, coin_added)

    _logger.info("Done")


    _logger.info("Processing challenges...")
    home = expanduser("~")
    challenges_path = home + "/challenges"
    start_number = int(os.environ.get("CHALLENGE_START_NUMBER", 0))
    stack = ChallengeStack.from_folder(folder_path=challenges_path, start_number=start_number)
    _logger.info(f"Created stack: {stack}")
    dare = Dare.from_file(home + "/dare.txt")
    last_timestamp = datetime.datetime.utcnow()
    _logger.info("Done")

    with ThermalPrinter(port='/dev/serial0') as printer:
        while True:
            if coinInserted and guard_interval_passed(last_timestamp):
                _logger.info("Coin inserted. New credit: {0:.2f}€".format(coinsValue / 100))
                msg = dare.compile(stack.pick(), stack.cur_count)
                _logger.info(msg)
                if ENABLE_PRINTING:
                    printer.out(msg, justify='C', strike=True)
                    printer.feed(2)
                else:
                    _logger.warning("Printing disabled! Set 'ENABLE_PRINTING' to True to enable it again!")
                last_timestamp = datetime.datetime.utcnow()
            coinInserted = False

if __name__ == "__main__":
    main()