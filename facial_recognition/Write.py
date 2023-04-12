#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

# function used when module is added to admin portal, write the name to the keycard, can be manually used to enter a name-- uncomment next line
# name = "THE_NAME"


def write_key(name):

    reader = SimpleMFRC522()
    reader.write(name)
    GPIO.cleanup()
    return f"Written {name}"


'''
#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()
try:
	text = input('New data:')
	print('Now place your tag to write')
	reader.write(text)
	print("Written")
finally:
	GPIO.cleanup()
'''
