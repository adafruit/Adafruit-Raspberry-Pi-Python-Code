#!/usr/bin/pythonhttp://raspberrypi.local/editor

#
# based on code from lrvick and LiquidCrystal
# lrvic - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp
#

from time import sleep
from Adafruit_I2C import Adafruit_I2C
from Adafruit_MCP230xx import Adafruit_MCP230XX
from Adafruit_CharLCDPlate import Adafruit_CharLCD

import smbus


# initialize the LCD (the pins are 'fixed', dont change the numbers!)

lcd = Adafruit_CharLCD(15, 13, [12,11,10,9], 14)
# clear display
lcd.clear()
# hello!
lcd.message("Adafruit RGB LCD\nPlate w/Keypad!")
sleep(1)

# first loop, just changes the color
lcd.backlight(lcd.RED)
sleep(.5)
lcd.backlight(lcd.YELLOW)
sleep(.5)
lcd.backlight(lcd.GREEN)
sleep(.5)
lcd.backlight(lcd.TEAL)
sleep(.5)
lcd.backlight(lcd.BLUE)
sleep(.5)
lcd.backlight(lcd.VIOLET)
sleep(.5)
lcd.backlight(lcd.ON)
sleep(.5)
lcd.backlight(lcd.OFF)
sleep(.5)

while 1:
	if (lcd.buttonPressed(lcd.LEFT)):
		lcd.clear()
		lcd.message("Red Red Wine")
		lcd.backlight(lcd.RED)

	if (lcd.buttonPressed(lcd.UP)):
		lcd.clear()
		lcd.message("Sita Sings \nthe blues")
		lcd.backlight(lcd.BLUE)

	if (lcd.buttonPressed(lcd.DOWN)):
		lcd.clear()
		lcd.message("I see fields\nof green");
		lcd.backlight(lcd.GREEN)

	if (lcd.buttonPressed(lcd.RIGHT)):
		lcd.clear()
		lcd.message("Purple mountain\n majesties");
		lcd.backlight(lcd.VIOLET)

	if (lcd.buttonPressed(lcd.SELECT)):
		lcd.clear()
		lcd.backlight(lcd.ON)


