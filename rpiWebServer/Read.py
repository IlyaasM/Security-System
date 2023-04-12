#!/usr/bin/env python

# This file is used as a module, to the admin portal, and can be used to manually input keycard to the DB
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import csv

reader = SimpleMFRC522()


def read_key():
    GPIO.setwarnings(False)
    try:
        id, text = reader.read()
        with open('DB.csv', 'a') as fd:
            fd.write(f"{id},{text}")
        print(id)
        print(text)
    finally:
        GPIO.cleanup()
# read_key()
