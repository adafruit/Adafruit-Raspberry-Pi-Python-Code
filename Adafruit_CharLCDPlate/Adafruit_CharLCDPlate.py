#!/usr/bin/python

# Based on code from lrvick and LiquidCrystal
# lrvic - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp

from Adafruit_MCP230xx import Adafruit_MCP230XX

class Adafruit_CharLCDPlate(Adafruit_MCP230XX):

    # Port expander input pin definitions
    SELECT                  = 0
    RIGHT                   = 1
    DOWN                    = 2
    UP                      = 3
    LEFT                    = 4

    # LED colors
    OFF                     = 0x00
    RED                     = 0x01
    GREEN                   = 0x02
    BLUE                    = 0x04
    YELLOW                  = RED + GREEN
    TEAL                    = GREEN + BLUE
    VIOLET                  = RED + BLUE
    WHITE                   = RED + GREEN + BLUE
    ON                      = RED + GREEN + BLUE

    # LCD Commands
    LCD_CLEARDISPLAY        = 0x01
    LCD_RETURNHOME          = 0x02
    LCD_ENTRYMODESET        = 0x04
    LCD_DISPLAYCONTROL      = 0x08
    LCD_CURSORSHIFT         = 0x10
    LCD_FUNCTIONSET         = 0x20
    LCD_SETCGRAMADDR        = 0x40
    LCD_SETDDRAMADDR        = 0x80

    # Flags for display on/off control
    LCD_DISPLAYON           = 0x04
    LCD_DISPLAYOFF          = 0x00
    LCD_CURSORON            = 0x02
    LCD_CURSOROFF           = 0x00
    LCD_BLINKON             = 0x01
    LCD_BLINKOFF            = 0x00

    # Flags for display entry mode
    LCD_ENTRYRIGHT          = 0x00
    LCD_ENTRYLEFT           = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # Flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE  = 0x00
    LCD_MOVERIGHT   = 0x04
    LCD_MOVELEFT    = 0x00


    def __init__(self, busnum=-1, addr=0x20, debug=False):

        self.mcp = Adafruit_MCP230XX(addr, 16, busnum, debug)

        for i in range(0,16):
            if i < 6:
                # Configure button lines as inputs w/pullups
                self.mcp.config(i, Adafruit_MCP230XX.INPUT)
                self.mcp.pullup(i, True)
            elif 9 <= i <= 12:
                # Configure LCD data lines as inputs w/o pullups
                self.mcp.config(i, Adafruit_MCP230XX.INPUT)
                self.mcp.pullup(i, False)
            else:
                # All other lines are outputs
                self.mcp.config(i, Adafruit_MCP230XX.OUTPUT)

        # Init control lines, backlight on (white)
        self.mcp.outputAll(0)

        self.displaycontrol  = (self.LCD_DISPLAYON |
                                self.LCD_CURSOROFF |
                                self.LCD_BLINKOFF)
        self.displaymode     = (self.LCD_ENTRYLEFT |
                                self.LCD_ENTRYSHIFTDECREMENT)
        self.displayshift    = (self.LCD_CURSORMOVE |
                                self.LCD_MOVERIGHT)

        self.write4(0x20) # Select 4-bit interface
        self.write4(0x28) # 2 line 5x8 matrix
        self.write4(self.LCD_CLEARDISPLAY)
        self.write4(self.LCD_CURSORSHIFT    | self.displayshift)
        self.write4(self.LCD_ENTRYMODESET   | self.displaymode)
        self.write4(self.LCD_DISPLAYCONTROL | self.displaycontrol)
        self.write4(self.LCD_RETURNHOME)


    # The LCD data pins (D4-D7) connect to MCP pins 12-9 (PORTB4-1), in
    # that order.  Because this sequence is 'reversed,' a direct shift
    # won't work.  This table remaps 4-bit data values to MCP PORTB
    # outputs, incorporating both the reverse and shift.
    flip = ( 0b00000000, 0b00010000, 0b00001000, 0b00011000,
             0b00000100, 0b00010100, 0b00001100, 0b00011100,
             0b00000010, 0b00010010, 0b00001010, 0b00011010,
             0b00000110, 0b00010110, 0b00001110, 0b00011110 )

    # Write 8-bit value to LCD over 4-bit interface
    def write4(self, value, char_mode=False):
        """ Send command/data to LCD """

        # The following code does not invoke the base class methods that
        # handle I/O exceptions.  Instead, the underlying smbus calls are
        # invoked directly for expediency, the expectation being that any
        # I2C access or address type errors have already been identified
        # during initialization.

        # The LCD control lines are all on MCP PORTB, so I2C byte ops
        # on that single port (rather than word ops on both PORTA and
        # PORTB together) are used here to save some bandwidth.
        # LCD pin RS  = MCP pin 15 (PORTB7)      Command/data
        # LCD pin RW  = MCP pin 14 (PORTB6)      Read/write
        # LCD pin E   = MCP pin 13 (PORTB5)      Strobe
        # LCD D4...D7 = MCP 12...9 (PORTB4...1)  Data (see notes later)

        # Poll LCD busy state until clear.  Data pins are inputs
        # by default, so no need to reconfigure I/O direction yet.

        #     Current PORTB pin state      RS=0          RW=1
        a = ((self.mcp.outputvalue >> 8) & 0b00000001) | 0b01000000
        b = a | 0b00100000 # E=1
        # Configure MCP lines for polling.  Will restore later.
        self.mcp.i2c.bus.write_byte_data(
          self.mcp.i2c.address, self.mcp.MCP23017_OLATB, a)
        while True:
            # Strobe high (enable)
            self.mcp.i2c.bus.write_byte_data(
              self.mcp.i2c.address, self.mcp.MCP23017_OLATB, b)
            # There's no need for delay calls when strobing, as the
            # limited I2C throughput already ensures the strobe is
            # held long enough.
            # First nybble contains busy state
            bits = self.mcp.i2c.bus.read_byte_data(
              self.mcp.i2c.address, self.mcp.MCP23017_GPIOB)
            # Strobe low (!enable)
            self.mcp.i2c.bus.write_byte_data(
              self.mcp.i2c.address, self.mcp.MCP23017_OLATB, a)
            if (bits & 0b00000010) == 0: break # D7=0, not busy
            # Ignore second nybble
            self.mcp.i2c.bus.write_byte_data(
              self.mcp.i2c.address, self.mcp.MCP23017_OLATB, b)
            self.mcp.i2c.bus.write_byte_data(
              self.mcp.i2c.address, self.mcp.MCP23017_OLATB, a)

        # Change data pins to outputs temporarily
        save = self.mcp.direction >> 8 # PORTB
        self.mcp.i2c.bus.write_byte_data(
          self.mcp.i2c.address, self.mcp.MCP23017_IODIRB, save & 0b11100001)

        a &= 0b00000001 # Mask out data bits & RW from current OLATB value
        if char_mode: a |= 0b10000000 # RS = Command/data

        b = a | self.flip[value >> 4] # Insert high 4 bits of data
        # Write initial !E state, data is sampled on rising strobe edge
        self.mcp.i2c.bus.write_byte_data(
          self.mcp.i2c.address, self.mcp.MCP23017_OLATB, b)
        # Strobe high
        self.mcp.i2c.bus.write_byte_data(
          self.mcp.i2c.address, self.mcp.MCP23017_OLATB, b | 0b00100000)
        # Strobe low
        self.mcp.i2c.bus.write_byte_data(
          self.mcp.i2c.address, self.mcp.MCP23017_OLATB, b)
        b = a | self.flip[value & 0x0F] # Insert low 4 bits
        self.mcp.i2c.bus.write_byte_data(
          self.mcp.i2c.address, self.mcp.MCP23017_OLATB, b)
        self.mcp.i2c.bus.write_byte_data(
          self.mcp.i2c.address, self.mcp.MCP23017_OLATB, b | 0b00100000)
        self.mcp.i2c.bus.write_byte_data(
          self.mcp.i2c.address, self.mcp.MCP23017_OLATB, b)

        # Change data pins back to inputs
        self.mcp.i2c.bus.write_byte_data(
          self.mcp.i2c.address, self.mcp.MCP23017_IODIRB, save)
        # And update mcp outputvalue state to reflect changes here
        self.mcp.outputvalue = (self.mcp.outputvalue & 0x00FF) | (b << 8)


    def begin(self, cols, lines):
        self.currline = 0
        self.numlines = lines
        self.clear()


    def clear(self):
        self.write4(self.LCD_CLEARDISPLAY)


    def home(self):
        self.write4(self.LCD_RETURNHOME)


    row_offsets = ( 0x00, 0x40, 0x14, 0x54 )
    def setCursor(self, col, row):
        if row > self.numlines: row = self.numlines - 1
        elif row < 0:           row = 0
        self.write4(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))


    def display(self):
        """ Turn the display on (quickly) """
        self.displaycontrol |= self.LCD_DISPLAYON
        self.write4(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noDisplay(self):
        """ Turn the display off (quickly) """
        self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write4(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def cursor(self):
        """ Underline cursor on """
        self.displaycontrol |= self.LCD_CURSORON
        self.write4(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noCursor(self):
        """ Underline cursor off """
        self.displaycontrol &= ~self.LCD_CURSORON
        self.write4(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def ToggleCursor(self):
        """ Toggles the underline cursor On/Off """
        self.displaycontrol ^= self.LCD_CURSORON
        self.write4(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def blink(self):
        """ Turn on the blinking cursor """
        self.displaycontrol |= self.LCD_BLINKON
        self.write4(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noBlink(self):
        """ Turn off the blinking cursor """
        self.displaycontrol &= ~self.LCD_BLINKON
        self.write4(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def ToggleBlink(self):
        """ Toggles the blinking cursor """
        self.displaycontrol ^= self.LCD_BLINKON
        self.write4(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def DisplayLeft(self):
        """ These commands scroll the display without changing the RAM """
        self.displayshift = self.LCD_DISPLAYMODE | self.LCD_MOVELEFT
        self.write4(self.LCD_CURSORSHIFT | self.displayshift)


    def scrollDisplayRight(self):
        """ These commands scroll the display without changing the RAM """
        self.displayshift = self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT
        self.write4(self.LCD_CURSORSHIFT | self.displayshift)


    def leftToRight(self):
        """ This is for text that flows left to right """
        self.displaymode |= self.LCD_ENTRYLEFT
        self.write4(self.LCD_ENTRYMODESET | self.displaymode)


    def rightToLeft(self):
        """ This is for text that flows right to left """
        self.displaymode &= ~self.LCD_ENTRYLEFT
        self.write4(self.LCD_ENTRYMODESET | self.displaymode)


    def autoscroll(self):
        """ This will 'right justify' text from the cursor """
        self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        self.write4(self.LCD_ENTRYMODESET | self.displaymode)


    def noAutoscroll(self):
        """ This will 'left justify' text from the cursor """
        self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write4(self.LCD_ENTRYMODESET | self.displaymode)


    def createChar(self, location, bitmap):
        self.write4(self.LCD_SETCGRAMADDR | ((location & 7) << 3))
        for i in range(8):
            self.write4(bitmap[i], True)
        self.write4(self.LCD_SETDDRAMADDR)


    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""
        for char in text:
            if char == '\n':
                self.write4(0xC0) # set DDRAM address to second line
            else:
                self.write4(ord(char), True)


    def backlight(self, color):
        n = ((self.mcp.outputvalue & 0b1111111000111111) |
             (((~color) & 0b111) << 6))
        # Direct smbus call so everything toggles together
        self.mcp.i2c.bus.write_word_data(
          self.mcp.i2c.address, self.mcp.MCP23017_OLATA, n)
        self.mcp.outputvalue = n


    def buttonPressed(self, b):
        return not self.mcp.input(b) if 0 <= b <= self.LEFT else False


if __name__ == '__main__':

    from time import sleep

    lcd = Adafruit_CharLCDPlate()
    lcd.begin(16, 2)
    lcd.clear()
    lcd.message("Adafruit RGB LCD\nPlate w/Keypad!")
    sleep(1)

    col = (('Red' , lcd.RED) , ('Yellow', lcd.YELLOW), ('Green' , lcd.GREEN),
           ('Teal', lcd.TEAL), ('Blue'  , lcd.BLUE)  , ('Violet', lcd.VIOLET),
           ('Off' , lcd.OFF) , ('On'    , lcd.ON))

    print "Cycle thru backlight colors"
    for c in col:
       print c[0]
       lcd.clear()
       lcd.message(c[0])
       lcd.backlight(c[1])
       sleep(0.5)

    btn = ((lcd.SELECT, 'Select', lcd.ON),
           (lcd.LEFT  , 'Left'  , lcd.RED),
           (lcd.UP    , 'Up'    , lcd.BLUE),
           (lcd.DOWN  , 'Down'  , lcd.GREEN),
           (lcd.RIGHT , 'Right' , lcd.VIOLET))
    
    print "Try buttons on plate"
    lcd.clear()
    lcd.message("Try buttons")
    prev = -1
    while True:
        for b in btn:
            if lcd.buttonPressed(b[0]):
                if b is not prev:
                    print b[1]
                    lcd.clear()
                    lcd.message(b[1])
                    lcd.backlight(b[2])
                    prev = b
                break
