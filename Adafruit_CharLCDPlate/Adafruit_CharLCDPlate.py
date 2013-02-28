#!/usr/bin/pythonhttp://raspberrypi.local/editor

#
# based on code from lrvick and LiquidCrystal
# lrvic - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp
#

from time import sleep
from Adafruit_I2C import Adafruit_I2C
from Adafruit_MCP230xx import Adafruit_MCP230XX
import smbus


class Adafruit_CharLCDPlate:

    OUTPUT = 0
    INPUT = 1
    
    # LED colors
    RED = 0x01
    GREEN = 0x02
    BLUE = 0x04
    YELLOW = 0x03
    TEAL = 0x06
    VIOLET = 0x05
    ON = 0x07
    OFF = 0x0

    # buttons
    SELECT = 0
    RIGHT = 1
    DOWN = 2
    UP = 3
    LEFT = 4

    # commands
    LCD_CLEARDISPLAY     	= 0x01
    LCD_RETURNHOME 		= 0x02
    LCD_ENTRYMODESET 		= 0x04
    LCD_DISPLAYCONTROL 		= 0x08
    LCD_CURSORSHIFT 		= 0x10
    LCD_FUNCTIONSET 		= 0x20
    LCD_SETCGRAMADDR 		= 0x40
    LCD_SETDDRAMADDR 		= 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT 		= 0x00
    LCD_ENTRYLEFT 		= 0x02
    LCD_ENTRYSHIFTINCREMENT 	= 0x01
    LCD_ENTRYSHIFTDECREMENT 	= 0x00

    # flags for display on/off control
    LCD_DISPLAYON 		= 0x04
    LCD_DISPLAYOFF 		= 0x00
    LCD_CURSORON 		= 0x02
    LCD_CURSOROFF 		= 0x00
    LCD_BLINKON 		= 0x01
    LCD_BLINKOFF 		= 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE 		= 0x08
    LCD_CURSORMOVE 		= 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE 		= 0x08
    LCD_CURSORMOVE 		= 0x00
    LCD_MOVERIGHT 		= 0x04
    LCD_MOVELEFT 		= 0x00

    # flags for function set
    LCD_8BITMODE 		= 0x10
    LCD_4BITMODE 		= 0x00
    LCD_2LINE 			= 0x08
    LCD_1LINE 			= 0x00
    LCD_5x10DOTS 		= 0x04
    LCD_5x8DOTS 		= 0x00




    def __init__(self, busnum=0, pin_rs=15, pin_e=13, pins_db=[12, 11, 10, 9], pin_rw=14):
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pin_rw = pin_rw
        self.pins_db = pins_db

	self.mcp = Adafruit_MCP230XX(busnum = busnum, address = 0x20, num_gpios = 16)

        self.mcp.config(self.pin_e, self.OUTPUT)
        self.mcp.config(self.pin_rs,  self.OUTPUT)
        self.mcp.config(self.pin_rw,  self.OUTPUT)
        self.mcp.output(self.pin_rw, 0)
        self.mcp.output(self.pin_e, 0)
        
        for pin in self.pins_db:
            self.mcp.config(pin,  self.OUTPUT)

	self.write4bits(0x33) # initialization
	self.write4bits(0x32) # initialization
	self.write4bits(0x28) # 2 line 5x7 matrix
	self.write4bits(0x0C) # turn cursor off 0x0E to enable cursor
	self.write4bits(0x06) # shift cursor right

	self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF

	self.displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS
	self.displayfunction |= self.LCD_2LINE

	""" Initialize to default text direction (for romance languages) """
	self.displaymode =  self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
	self.write4bits(self.LCD_ENTRYMODESET | self.displaymode) #  set the entry mode

	# turn on backlights!
    	self.mcp.config(6, self.mcp.OUTPUT)
    	self.mcp.config(7, self.mcp.OUTPUT)
    	self.mcp.config(8, self.mcp.OUTPUT)
    	self.mcp.output(6, 0) # red
    	self.mcp.output(7, 0) # green 
    	self.mcp.output(8, 0) # blue

	# turn on pullups
        self.mcp.pullup(self.SELECT, True)
        self.mcp.pullup(self.LEFT, True)
        self.mcp.pullup(self.RIGHT, True)
        self.mcp.pullup(self.UP, True)
        self.mcp.pullup(self.DOWN, True)
	self.mcp.config(self.SELECT, self.mcp.INPUT)
	self.mcp.config(self.LEFT, self.mcp.INPUT)
	self.mcp.config(self.RIGHT, self.mcp.INPUT)
	self.mcp.config(self.DOWN, self.mcp.INPUT)
	self.mcp.config(self.UP, self.mcp.INPUT)

    def begin(self, cols, lines):
        if (lines > 1):
            self.numlines = lines
            self.displayfunction |= self.LCD_2LINE
        self.currline = 0
        self.clear()

    def home(self):
        self.write4bits(self.LCD_RETURNHOME) # set cursor position to zero
        self.delayMicroseconds(2000) # this command takes a long time!

    def clear(self):
        self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
        self.delayMicroseconds(2000)	# 2000 microsecond sleep, clearing the display takes a long time

    def setCursor(self, col, row):
        self.row_offsets = [ 0x00, 0x40, 0x14, 0x54 ]
        if ( row > self.numlines ): 
		    row = self.numlines - 1 # we count rows starting w/0
        self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

    def noDisplay(self): 
        """ Turn the display off (quickly) """
        self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def display(self):
        """ Turn the display on (quickly) """
        self.displaycontrol |= self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def noCursor(self):
        """ Turns the underline cursor on/off """
        self.displaycontrol &= ~self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def cursor(self):
        """ Cursor On """
        self.displaycontrol |= self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def noBlink(self):
	""" Turn on and off the blinking cursor """
        self.displaycontrol &= ~self.LCD_BLINKON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def noBlink(self):
	""" Turn on and off the blinking cursor """
        self.displaycontrol &= ~self.LCD_BLINKON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def DisplayLeft(self):
        """ These commands scroll the display without changing the RAM """
        self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)

    def scrollDisplayRight(self):
	""" These commands scroll the display without changing the RAM """
        self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT);

    def leftToRight(self):
	""" This is for text that flows Left to Right """
        self.displaymode |= self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode);

    def rightToLeft(self):
	""" This is for text that flows Right to Left """
        self.displaymode &= ~self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def autoscroll(self):
	""" This will 'right justify' text from the cursor """
        self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def noAutoscroll(self): 
	""" This will 'left justify' text from the cursor """
        self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def createChar(self, location, bitmap):
        self.write4bits(self.LCD_SETCGRAMADDR | ((location & 7) << 3))
        for i in range(8):
            self.write4bits(bitmap[i], True)
        self.write4bits(self.LCD_SETDDRAMADDR)

    def write4bits(self, bits, char_mode=False):
        """ Send command to LCD """
        #self.delayMicroseconds(1000) # 1000 microsecond sleep
        bits=bin(bits)[2:].zfill(8)
        self.mcp.output(self.pin_rs, char_mode)

        for i in range(4):
            if bits[i] == "1":
                self.mcp.output(self.pins_db[::-1][i], True)
            else:
                self.mcp.output(self.pins_db[::-1][i], False)
        self.pulseEnable()

        for i in range(4,8):
            if bits[i] == "1":
                self.mcp.output(self.pins_db[::-1][i-4], True)
            else:
                self.mcp.output(self.pins_db[::-1][i-4], False)
        self.pulseEnable()

    def delayMicroseconds(self, microseconds):
        seconds = microseconds / 1000000	# divide microseconds by 1 million for seconds
        sleep(seconds)

    def pulseEnable(self):
        self.mcp.output(self.pin_e, True)
        self.delayMicroseconds(1)		# 1 microsecond pause - enable pulse must be > 450ns 
        self.mcp.output(self.pin_e, False)
        #self.delayMicroseconds(1)		# commands need > 37us to settle

    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""
        for char in text:
            if char == '\n':
                self.write4bits(0xC0) # next line
            else:
                self.write4bits(ord(char),True)

    def backlight(self, color):
	self.mcp.output(6, not color & 0x01)
	self.mcp.output(7, not color & 0x02)
	self.mcp.output(8, not color & 0x04)

    def buttonPressed(self, buttonname):
	if (buttonname > self.LEFT): 
		return false

	return not self.mcp.input(buttonname)


if __name__ == '__main__':

    lcd = Adafruit_CharLCDPlate(busnum = 0)
    lcd.clear()
    lcd.message("Adafruit RGB LCD\nPlate w/Keypad!")
    sleep(1)
    while 1:
	if (lcd.buttonPressed(lcd.LEFT)):
		lcd.backlight(lcd.RED)

	if (lcd.buttonPressed(lcd.UP)):
		lcd.backlight(lcd.BLUE)

	if (lcd.buttonPressed(lcd.DOWN)):
		lcd.backlight(lcd.GREEN)

	if (lcd.buttonPressed(lcd.RIGHT)):
		lcd.backlight(lcd.VIOLET)

	if (lcd.buttonPressed(lcd.SELECT)):
		lcd.backlight(lcd.ON)


    while 1:
	lcd.backlight(lcd.RED)
	sleep(1)
	lcd.backlight(lcd.YELLOW)
	sleep(1)
	lcd.backlight(lcd.GREEN)
	sleep(1)
	lcd.backlight(lcd.TEAL)
	sleep(1)
	lcd.backlight(lcd.BLUE)
	sleep(1)
	lcd.backlight(lcd.VIOLET)
	sleep(1)
	lcd.backlight(lcd.ON)
	sleep(1)
	lcd.backlight(lcd.OFF)
	sleep(1)
