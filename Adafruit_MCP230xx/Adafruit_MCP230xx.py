#!/usr/bin/python

# Copyright 2012 Daniel Berlin (with some changes by Adafruit Industries/Limor Fried)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal  MCP230XX_GPIO(1, 0xin
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from Adafruit_I2C import Adafruit_I2C
import smbus
import time

MCP23017_IODIRA = 0x00
MCP23017_IODIRB = 0x01
MCP23017_GPIOA  = 0x12
MCP23017_GPIOB  = 0x13
MCP23017_GPPUA  = 0x0C
MCP23017_GPPUB  = 0x0D
MCP23017_OLATA  = 0x14
MCP23017_OLATB  = 0x15
MCP23008_GPIOA  = 0x09
MCP23008_GPPUA  = 0x06
MCP23008_OLATA  = 0x0A

class Adafruit_MCP230XX(object):
    OUTPUT = 0
    INPUT = 1

    def __init__(self, address, num_gpios, busnum = 0):
        assert num_gpios >= 0 and num_gpios <= 16, "Number of GPIOs must be between 0 and 16"
        self.i2c = Adafruit_I2C(address=address, bus=smbus.SMBus(busnum))     
        self.address = address
        self.num_gpios = num_gpios

        # set defaults
        if num_gpios <= 8:
            self.i2c.write8(MCP23017_IODIRA, 0xFF)  # all inputs on port A
            self.direction = self.i2c.readU8(MCP23017_IODIRA)
            self.i2c.write8(MCP23008_GPPUA, 0x00)
        elif num_gpios > 8 and num_gpios <= 16:
            self.i2c.write8(MCP23017_IODIRA, 0xFF)  # all inputs on port A
            self.i2c.write8(MCP23017_IODIRB, 0xFF)  # all inputs on port B
            self.direction = self.i2c.readU8(MCP23017_IODIRA)
            self.direction |= self.i2c.readU8(MCP23017_IODIRB) << 8
            self.i2c.write8(MCP23017_GPPUA, 0x00)
            self.i2c.write8(MCP23017_GPPUB, 0x00)

    
    def _changebit(self, bitmap, bit, value):
        assert value == 1 or value == 0, "Value is %s must be 1 or 0" % value
        if value == 0:
            return bitmap & ~(1 << bit)
        elif value == 1:
            return bitmap | (1 << bit)

    def _readandchangepin(self, port, pin, value, currvalue = None):
        assert pin >= 0 and pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        #assert self.direction & (1 << pin) == 0, "Pin %s not set to output" % pin
        if not currvalue:
            currvalue = self.i2c.readU8(port)
        newvalue = self._changebit(currvalue, pin, value)
        self.i2c.write8(port, newvalue)
        return newvalue


    def pullup(self, pin, value):
        if self.num_gpios <= 8:
            return self._readandchangepin(MCP23008_GPPUA, pin, value)
        if self.num_gpios <= 16:
            if (pin < 8):
                return self._readandchangepin(MCP23017_GPPUA, pin, value)
            else:
                return self._readandchangepin(MCP23017_GPPUB, pin-8, value)

    # Set pin to either input or output mode
    def config(self, pin, mode):        
        if self.num_gpios <= 8:
            self.direction = self._readandchangepin(MCP23017_IODIRA, pin, mode)
        if self.num_gpios <= 16:
            if (pin < 8):
                # replace low bits
                self.direction = (self.direction & 0xff00) |  self._readandchangepin(MCP23017_IODIRA, pin, mode)
            else:
                # replace hi bits
                self.direction = (self.direction & 0xff) | self._readandchangepin(MCP23017_IODIRB, pin-8, mode) << 8
        #print "config ", pin, mode, self.direction, bin(self.direction)[2:].zfill(16)
        return self.direction

    def output(self, pin, value):
        # assert self.direction & (1 << pin) == 0, "Pin %s not set to output" % pin
        if self.num_gpios <= 8:
            self.outputvalue = self._readandchangepin(MCP23008_GPIOA, pin, value, self.i2c.readU8(MCP23008_OLATA))
        if self.num_gpios <= 16:
            if (pin < 8):
                self.outputvalue = self._readandchangepin(MCP23017_GPIOA, pin, value, self.i2c.readU8(MCP23017_OLATA))
            else:
                self.outputvalue = self._readandchangepin(MCP23017_GPIOB, pin-8, value, self.i2c.readU8(MCP23017_OLATB))
        return self.outputvalue

# inaccessible code removed from here
        
    def input(self, pin, check=True):
        assert pin >= 0 and pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        if check:
            assert self.direction & (1 << pin) != 0, "Pin %s not set to input" % pin
        if self.num_gpios <= 8:
            value = self.i2c.readU8(MCP23008_GPIOA)
        elif self.num_gpios > 8 and self.num_gpios <= 16:
            value = self.i2c.readU16(MCP23017_GPIOA)
            temp = value >> 8
            value <<= 8
            value |= temp
        return (value & (1 << pin))>>pin # to make 0 or 1
    

 
# these were indented so  within scope of input but have now made them all part of the class
# have modified so can read any address but default to those given in original code
# also use available routines in imported Adafruit_I2C class
    def readU8(self, add=MCP23008_OLATA):
        result = self.i2c.readU8(add)
        return(result)

    def readS8(self, add=MCP23008_OLATA):
        result = self.i2c.readS8(add)
        return result

    def readU16(self, add=MCP23017_OLATA):
        assert self.num_gpios >= 16, "16bits required"
        result = self.i2c.readU16(add)
        return result

    def readS16(self, add=MCP23017_OLATA):
        assert self.num_gpios >= 16, "16bits required"
        result = self.i2c.readS16(add)
        return result

    def write8(self, value, add=MCP23008_OLATA):
        self.i2c.write8(add, value)

    def write16(self, value, add=MCP23017_OLATA):
        assert self.num_gpios >= 16, "16bits required"
        self.i2c.write16(add, value)
      

# RPi.GPIO compatible interface for MCP23017 and MCP23008

class MCP230XX_GPIO(object):
    OUT = 0
    IN = 1
    BCM = 0
    BOARD = 0
    def __init__(self, busnum, address, num_gpios):
        self.chip = Adafruit_MCP230XX(busnum, address, num_gpios)
    def setmode(self, mode):
        # do nothing
        pass
    def setup(self, pin, mode):
        self.chip.config(pin, mode)
    def input(self, pin):
        return self.chip.input(pin)
    def output(self, pin, value):
        self.chip.output(pin, value)
    def pullup(self, pin, value):
        self.chip.pullup(pin, value)
        

if __name__ == '__main__':
    mcp = Adafruit_MCP230XX(address = 0x20, num_gpios = 8)

    # ***************************************************
    # Set num_gpios to 8 for MCP23008 or 16 for MCP23017!
    # If you have a new Pi you may also need to add:
    # busnum = 1
    # ***************************************************
    
    # Set pins 0, 1 and 2 to output (you can set pins 0..15 this way)
    mcp.config(0, mcp.OUTPUT)
    mcp.config(1, mcp.OUTPUT)
    mcp.config(2, mcp.OUTPUT)
    
    # Set pin 3 to input with the pullup resistor enabled
    mcp.pullup(3, 1)
    # Read pin 3 and display the results
    print "%d: %x" % (3, mcp.input(3) >> 3)
    
    # Python speed test on output 0 toggling at max speed
    while (True):
      mcp.output(0, 1)  # Pin 0 High
      mcp.output(0, 0)  # Pin 0 Low
