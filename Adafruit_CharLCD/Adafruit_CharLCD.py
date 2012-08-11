#!/usr/bin/python

#
# based on code from lrvick and LiquidCrystal
# lrvic - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp
#

import RPi.GPIO as GPIO
from time import sleep

class Adafruit_CharLCD:

    def __init__(self, pin_rs=24, pin_e=23, pins_db=[17, 21, 22, 25]):

        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_e, GPIO.OUT)
        GPIO.setup(self.pin_rs, GPIO.OUT)

        for pin in self.pins_db:
            GPIO.setup(pin, GPIO.OUT)

	self.write4bits(0x33) # initialization
	self.write4bits(0x32) # initialization
	self.write4bits(0x28) # 2 line 5x7 matrix
	self.write4bits(0x0C) # turn cursor off 0x0E to enable cursor
	self.write4bits(0x06) # shift cursor right
        self.clear()
	

    def clear(self):

	self.write4bits(0x01) # command to clear display

	# 2000 microsecond sleep, clearing the display takes a long time
	sleep(.002)
	#self.delayMicroseconds(2000)

    def write4bits(self, bits, char_mode=False):
        """ Send command to LCD """

	# 1000 microseconds sleep
	# sleep(.001)
	self.delayMicroseconds(1000)

        bits=bin(bits)[2:].zfill(8)

        GPIO.output(self.pin_rs, char_mode)

        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i], True)

	self.pulseEnable()

        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4,8):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i-4], True)

	self.pulseEnable()


    def delayMicroseconds(self, microseconds):
	seconds = microseconds / 1000000	# divide microseconds by 1 million for seconds
	sleep(seconds)


    def pulseEnable(self):
	GPIO.output(self.pin_e, False)
	self.delayMicroseconds(1)		# 1 microsecond pause - enable pulse must be > 450ns 
	GPIO.output(self.pin_e, True)
	self.delayMicroseconds(1)		# 1 microsecond pause - enable pulse must be > 450ns 
	GPIO.output(self.pin_e, False)
	self.delayMicroseconds(1)		# commands need > 37us to settle


    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""

        for char in text:
            if char == '\n':
                self.write4bits(0xC0) # next line
            else:
                self.write4bits(ord(char),True)


if __name__ == '__main__':

    lcd = Adafruit_CharLCD()

    lcd.clear()
    lcd.message("  Adafruit 16x2\n Standard LCD")

