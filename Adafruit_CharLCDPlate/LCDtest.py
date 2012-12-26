#!/usr/bin/python

from time import sleep
from Adafruit_I2C import Adafruit_I2C
from Adafruit_MCP230xx import Adafruit_MCP230XX
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

import smbus


# initialize the LCD plate
# use busnum = 0 for raspi version 1 (256MB) and busnum = 1 for version 2
lcd = Adafruit_CharLCDPlate(busnum = 0)

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


