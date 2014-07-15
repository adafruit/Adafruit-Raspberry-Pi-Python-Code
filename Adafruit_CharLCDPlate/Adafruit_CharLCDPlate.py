#!/usr/bin/python

# Python library for Adafruit RGB-backlit LCD plate for Raspberry Pi.
# Written by Adafruit Industries.  MIT license.

# This is essentially a complete rewrite, but the calling syntax
# and constants are based on code from lrvick and LiquidCrystal.
# lrvic - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp

from Adafruit_I2C import Adafruit_I2C
from time import sleep


class Adafruit_CharLCDPlate(Adafruit_I2C):

    # ----------------------------------------------------------------------
    # Constants

    # Port expander registers
    MCP23017_IOCON_BANK0    = 0x0A  # IOCON when Bank 0 active
    MCP23017_IOCON_BANK1    = 0x15  # IOCON when Bank 1 active
    # These are register addresses when in Bank 1 only:
    MCP23017_GPIOA          = 0x09
    MCP23017_IODIRB         = 0x10
    MCP23017_GPIOB          = 0x19

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

    # Line addresses for up to 4 line displays.  Maps line number to DDRAM address for line.
    LINE_ADDRESSES = { 1: 0xC0, 2: 0x94, 3: 0xD4 }

    # Truncation constants for message function truncate parameter.
    NO_TRUNCATE       = 0
    TRUNCATE          = 1
    TRUNCATE_ELLIPSIS = 2

    # ----------------------------------------------------------------------
    # Constructor

    def __init__(self, busnum=-1, addr=0x20, debug=False, backlight=ON):

        self.i2c = Adafruit_I2C(addr, busnum, debug)

        # I2C is relatively slow.  MCP output port states are cached
        # so we don't need to constantly poll-and-change bit states.
        self.porta, self.portb, self.ddrb = 0, 0, 0b00000010

        # Set initial backlight color.
        c          = ~backlight
        self.porta = (self.porta & 0b00111111) | ((c & 0b011) << 6)
        self.portb = (self.portb & 0b11111110) | ((c & 0b100) >> 2)

        # Set MCP23017 IOCON register to Bank 0 with sequential operation.
        # If chip is already set for Bank 0, this will just write to OLATB,
        # which won't seriously bother anything on the plate right now
        # (blue backlight LED will come on, but that's done in the next
        # step anyway).
        self.i2c.bus.write_byte_data(
          self.i2c.address, self.MCP23017_IOCON_BANK1, 0)

        # Brute force reload ALL registers to known state.  This also
        # sets up all the input pins, pull-ups, etc. for the Pi Plate.
        self.i2c.bus.write_i2c_block_data(
          self.i2c.address, 0, 
          [ 0b00111111,   # IODIRA    R+G LEDs=outputs, buttons=inputs
            self.ddrb ,   # IODIRB    LCD D7=input, Blue LED=output
            0b00111111,   # IPOLA     Invert polarity on button inputs
            0b00000000,   # IPOLB
            0b00000000,   # GPINTENA  Disable interrupt-on-change
            0b00000000,   # GPINTENB
            0b00000000,   # DEFVALA
            0b00000000,   # DEFVALB
            0b00000000,   # INTCONA
            0b00000000,   # INTCONB
            0b00000000,   # IOCON
            0b00000000,   # IOCON
            0b00111111,   # GPPUA     Enable pull-ups on buttons
            0b00000000,   # GPPUB
            0b00000000,   # INTFA
            0b00000000,   # INTFB
            0b00000000,   # INTCAPA
            0b00000000,   # INTCAPB
            self.porta,   # GPIOA
            self.portb,   # GPIOB
            self.porta,   # OLATA
            self.portb ]) # OLATB

        # Switch to Bank 1 and disable sequential operation.
        # From this point forward, the register addresses do NOT match
        # the list immediately above.  Instead, use the constants defined
        # at the start of the class.  Also, the address register will no
        # longer increment automatically after this -- multi-byte
        # operations must be broken down into single-byte calls.
        self.i2c.bus.write_byte_data(
          self.i2c.address, self.MCP23017_IOCON_BANK0, 0b10100000)

        self.displayshift   = (self.LCD_CURSORMOVE |
                               self.LCD_MOVERIGHT)
        self.displaymode    = (self.LCD_ENTRYLEFT |
                               self.LCD_ENTRYSHIFTDECREMENT)
        self.displaycontrol = (self.LCD_DISPLAYON |
                               self.LCD_CURSOROFF |
                               self.LCD_BLINKOFF)

        self.write(0x33) # Init
        self.write(0x32) # Init
        self.write(0x28) # 2 line 5x8 matrix
        self.write(self.LCD_CLEARDISPLAY)
        self.write(self.LCD_CURSORSHIFT    | self.displayshift)
        self.write(self.LCD_ENTRYMODESET   | self.displaymode)
        self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)
        self.write(self.LCD_RETURNHOME)


    # ----------------------------------------------------------------------
    # Write operations

    # The LCD data pins (D4-D7) connect to MCP pins 12-9 (PORTB4-1), in
    # that order.  Because this sequence is 'reversed,' a direct shift
    # won't work.  This table remaps 4-bit data values to MCP PORTB
    # outputs, incorporating both the reverse and shift.
    flip = ( 0b00000000, 0b00010000, 0b00001000, 0b00011000,
             0b00000100, 0b00010100, 0b00001100, 0b00011100,
             0b00000010, 0b00010010, 0b00001010, 0b00011010,
             0b00000110, 0b00010110, 0b00001110, 0b00011110 )

    # Low-level 4-bit interface for LCD output.  This doesn't actually
    # write data, just returns a byte array of the PORTB state over time.
    # Can concatenate the output of multiple calls (up to 8) for more
    # efficient batch write.
    def out4(self, bitmask, value):
        hi = bitmask | self.flip[value >> 4]
        lo = bitmask | self.flip[value & 0x0F]
        return [hi | 0b00100000, hi, lo | 0b00100000, lo]


    # The speed of LCD accesses is inherently limited by I2C through the
    # port expander.  A 'well behaved program' is expected to poll the
    # LCD to know that a prior instruction completed.  But the timing of
    # most instructions is a known uniform 37 mS.  The enable strobe
    # can't even be twiddled that fast through I2C, so it's a safe bet
    # with these instructions to not waste time polling (which requires
    # several I2C transfers for reconfiguring the port direction).
    # The D7 pin is set as input when a potentially time-consuming
    # instruction has been issued (e.g. screen clear), as well as on
    # startup, and polling will then occur before more commands or data
    # are issued.

    pollables = ( LCD_CLEARDISPLAY, LCD_RETURNHOME )

    # Write byte, list or string value to LCD
    def write(self, value, char_mode=False):
        """ Send command/data to LCD """

        # If pin D7 is in input state, poll LCD busy flag until clear.
        if self.ddrb & 0b00000010:
            lo = (self.portb & 0b00000001) | 0b01000000
            hi = lo | 0b00100000 # E=1 (strobe)
            self.i2c.bus.write_byte_data(
              self.i2c.address, self.MCP23017_GPIOB, lo)
            while True:
                # Strobe high (enable)
                self.i2c.bus.write_byte(self.i2c.address, hi)
                # First nybble contains busy state
                bits = self.i2c.bus.read_byte(self.i2c.address)
                # Strobe low, high, low.  Second nybble (A3) is ignored.
                self.i2c.bus.write_i2c_block_data(
                  self.i2c.address, self.MCP23017_GPIOB, [lo, hi, lo])
                if (bits & 0b00000010) == 0: break # D7=0, not busy
            self.portb = lo

            # Polling complete, change D7 pin to output
            self.ddrb &= 0b11111101
            self.i2c.bus.write_byte_data(self.i2c.address,
              self.MCP23017_IODIRB, self.ddrb)

        bitmask = self.portb & 0b00000001   # Mask out PORTB LCD control bits
        if char_mode: bitmask |= 0b10000000 # Set data bit if not a command

        # If string or list, iterate through multiple write ops
        if isinstance(value, str):
            last = len(value) - 1 # Last character in string
            data = []             # Start with blank list
            for i, v in enumerate(value): # For each character...
                # Append 4 bytes to list representing PORTB over time.
                # First the high 4 data bits with strobe (enable) set
                # and unset, then same with low 4 data bits (strobe 1/0).
                data.extend(self.out4(bitmask, ord(v)))
                # I2C block data write is limited to 32 bytes max.
                # If limit reached, write data so far and clear.
                # Also do this on last byte if not otherwise handled.
                if (len(data) >= 32) or (i == last):
                    self.i2c.bus.write_i2c_block_data(
                      self.i2c.address, self.MCP23017_GPIOB, data)
                    self.portb = data[-1] # Save state of last byte out
                    data       = []       # Clear list for next iteration
        elif isinstance(value, list):
            # Same as above, but for list instead of string
            last = len(value) - 1
            data = []
            for i, v in enumerate(value):
                data.extend(self.out4(bitmask, v))
                if (len(data) >= 32) or (i == last):
                    self.i2c.bus.write_i2c_block_data(
                      self.i2c.address, self.MCP23017_GPIOB, data)
                    self.portb = data[-1]
                    data       = []
        else:
            # Single byte
            data = self.out4(bitmask, value)
            self.i2c.bus.write_i2c_block_data(
              self.i2c.address, self.MCP23017_GPIOB, data)
            self.portb = data[-1]

        # If a poll-worthy instruction was issued, reconfigure D7
        # pin as input to indicate need for polling on next call.
        if (not char_mode) and (value in self.pollables):
            self.ddrb |= 0b00000010
            self.i2c.bus.write_byte_data(self.i2c.address,
              self.MCP23017_IODIRB, self.ddrb)


    # ----------------------------------------------------------------------
    # Utility methods

    def begin(self, cols, lines):
        self.currline = 0
        self.numlines = lines
        self.numcols = cols
        self.clear()


    # Puts the MCP23017 back in Bank 0 + sequential write mode so
    # that other code using the 'classic' library can still work.
    # Any code using this newer version of the library should
    # consider adding an atexit() handler that calls this.
    def stop(self):
        self.porta = 0b11000000  # Turn off LEDs on the way out
        self.portb = 0b00000001
        sleep(0.0015)
        self.i2c.bus.write_byte_data(
          self.i2c.address, self.MCP23017_IOCON_BANK1, 0)
        self.i2c.bus.write_i2c_block_data(
          self.i2c.address, 0, 
          [ 0b00111111,   # IODIRA
            self.ddrb ,   # IODIRB
            0b00000000,   # IPOLA
            0b00000000,   # IPOLB
            0b00000000,   # GPINTENA
            0b00000000,   # GPINTENB
            0b00000000,   # DEFVALA
            0b00000000,   # DEFVALB
            0b00000000,   # INTCONA
            0b00000000,   # INTCONB
            0b00000000,   # IOCON
            0b00000000,   # IOCON
            0b00111111,   # GPPUA
            0b00000000,   # GPPUB
            0b00000000,   # INTFA
            0b00000000,   # INTFB
            0b00000000,   # INTCAPA
            0b00000000,   # INTCAPB
            self.porta,   # GPIOA
            self.portb,   # GPIOB
            self.porta,   # OLATA
            self.portb ]) # OLATB


    def clear(self):
        self.write(self.LCD_CLEARDISPLAY)


    def home(self):
        self.write(self.LCD_RETURNHOME)


    row_offsets = ( 0x00, 0x40, 0x14, 0x54 )
    def setCursor(self, col, row):
        if row > self.numlines: row = self.numlines - 1
        elif row < 0:           row = 0
        self.write(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))


    def display(self):
        """ Turn the display on (quickly) """
        self.displaycontrol |= self.LCD_DISPLAYON
        self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noDisplay(self):
        """ Turn the display off (quickly) """
        self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def cursor(self):
        """ Underline cursor on """
        self.displaycontrol |= self.LCD_CURSORON
        self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noCursor(self):
        """ Underline cursor off """
        self.displaycontrol &= ~self.LCD_CURSORON
        self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def ToggleCursor(self):
        """ Toggles the underline cursor On/Off """
        self.displaycontrol ^= self.LCD_CURSORON
        self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def blink(self):
        """ Turn on the blinking cursor """
        self.displaycontrol |= self.LCD_BLINKON
        self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noBlink(self):
        """ Turn off the blinking cursor """
        self.displaycontrol &= ~self.LCD_BLINKON
        self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def ToggleBlink(self):
        """ Toggles the blinking cursor """
        self.displaycontrol ^= self.LCD_BLINKON
        self.write(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def scrollDisplayLeft(self):
        """ These commands scroll the display without changing the RAM """
        self.displayshift = self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT
        self.write(self.LCD_CURSORSHIFT | self.displayshift)


    def scrollDisplayRight(self):
        """ These commands scroll the display without changing the RAM """
        self.displayshift = self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT
        self.write(self.LCD_CURSORSHIFT | self.displayshift)


    def leftToRight(self):
        """ This is for text that flows left to right """
        self.displaymode |= self.LCD_ENTRYLEFT
        self.write(self.LCD_ENTRYMODESET | self.displaymode)


    def rightToLeft(self):
        """ This is for text that flows right to left """
        self.displaymode &= ~self.LCD_ENTRYLEFT
        self.write(self.LCD_ENTRYMODESET | self.displaymode)


    def autoscroll(self):
        """ This will 'right justify' text from the cursor """
        self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        self.write(self.LCD_ENTRYMODESET | self.displaymode)


    def noAutoscroll(self):
        """ This will 'left justify' text from the cursor """
        self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write(self.LCD_ENTRYMODESET | self.displaymode)


    def createChar(self, location, bitmap):
        self.write(self.LCD_SETCGRAMADDR | ((location & 7) << 3))
        self.write(bitmap, True)
        self.write(self.LCD_SETDDRAMADDR)


    def message(self, text, truncate=NO_TRUNCATE):
        """ Send string to LCD. Newline wraps to second line"""
        lines = str(text).split('\n')    # Split at newline(s)
        for i, line in enumerate(lines): # For each substring...
            address = self.LINE_ADDRESSES.get(i, None)
            if address is not None:      # If newline(s),
                self.write(address)      #  set DDRAM address to line
            # Handle appropriate truncation if requested.
            linelen = len(line)
            if truncate == self.TRUNCATE and linelen > self.numcols:
                # Hard truncation of line.
                self.write(line[0:self.numcols], True)
            elif truncate == self.TRUNCATE_ELLIPSIS and linelen > self.numcols:
                # Nicer truncation with ellipses.
                self.write(line[0:self.numcols-3] + '...', True)
            else:
                self.write(line, True)



    def backlight(self, color):
        c          = ~color
        self.porta = (self.porta & 0b00111111) | ((c & 0b011) << 6)
        self.portb = (self.portb & 0b11111110) | ((c & 0b100) >> 2)
        # Has to be done as two writes because sequential operation is off.
        self.i2c.bus.write_byte_data(
          self.i2c.address, self.MCP23017_GPIOA, self.porta)
        self.i2c.bus.write_byte_data(
          self.i2c.address, self.MCP23017_GPIOB, self.portb)


    # Read state of single button
    def buttonPressed(self, b):
        return (self.i2c.readU8(self.MCP23017_GPIOA) >> b) & 1


    # Read and return bitmask of combined button state
    def buttons(self):
        return self.i2c.readU8(self.MCP23017_GPIOA) & 0b11111


    # ----------------------------------------------------------------------
    # Test code

if __name__ == '__main__':

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
