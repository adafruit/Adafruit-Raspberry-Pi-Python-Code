#!/usr/bin/python

# Copyright 2012 Daniel Berlin (with some changes by Limor Fried,
# Adafruit Industries)

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from Adafruit_I2C import Adafruit_I2C

class Adafruit_MCP230XX(Adafruit_I2C):

    INPUT  = True
    OUTPUT = False

    MCP23017_IODIRA = 0x00
    MCP23017_IODIRB = 0x01
    MCP23017_GPPUA  = 0x0C
    MCP23017_GPPUB  = 0x0D
    MCP23017_GPIOA  = 0x12
    MCP23017_GPIOB  = 0x13
    MCP23017_OLATA  = 0x14
    MCP23017_OLATB  = 0x15
    MCP23008_IODIR  = 0x00
    MCP23008_GPIO   = 0x09
    MCP23008_GPPU   = 0x06
    MCP23008_OLAT   = 0x0A


    def __init__(self, address, num_gpios=8, busnum=-1, debug=False):

        assert 0 < num_gpios < 17, "Number of GPIOs must be between 1 and 16"

        self.i2c       = Adafruit_I2C(address, busnum, debug)
        self.num_gpios = num_gpios
        self.pullups   = 0

        # Set default pin values -- all inputs with pull-ups disabled.
        # Current OLAT (output) value is polled, not set.
        if num_gpios <= 8:
            self.direction = 0xFF
            self.i2c.write8(self.MCP23008_IODIR, self.direction)
            self.i2c.write8(self.MCP23008_GPPU , self.pullups)
            self.outputvalue = self.i2c.readU8(self.MCP23008_OLAT)
        else:
            self.direction = 0xFFFF
            self.i2c.write16(self.MCP23017_IODIRA, self.direction)
            self.i2c.write16(self.MCP23017_GPPUA , self.pullups)
            self.outputvalue = self.i2c.readU16(self.MCP23017_OLATA)


    # Set single pin to either INPUT or OUTPUT mode
    def config(self, pin, mode):

        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, must be between 0 and %s" % (pin, self.num_gpios-1)

        if mode is self.INPUT: self.direction |=  (1 << pin)
        else:                  self.direction &= ~(1 << pin)

        if self.num_gpios <= 8:
            self.i2c.write8(self.MCP23008_IODIR, self.direction)
        elif pin < 8:
            # Replace low bits (IODIRA)
            self.i2c.write8(self.MCP23017_IODIRA, self.direction & 0xFF)
        else:
            # Replace high bits (IODIRB)
            self.i2c.write8(self.MCP23017_IODIRB, self.direction >> 8)

        return self.direction


    # Enable pull-up resistor on single input pin
    def pullup(self, pin, enable, check=False):

        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, must be between 0 and %s" % (pin, self.num_gpios-1)
        if check:
            assert (self.direction & (1 << pin)) != 0, "Pin %s not set to input" % pin

        if enable: self.pullups |=  (1 << pin)
        else:      self.pullups &= ~(1 << pin)

        if self.num_gpios <= 8:
            self.i2c.write8(self.MCP23008_GPPU, self.pullups)
        elif pin < 8:
            # Replace low bits (GPPUA)
            self.i2c.write8(self.MCP23017_GPPUA, self.pullups & 0xFF)
        else:
            # Replace high bits (GPPUB)
            self.i2c.write8(self.MCP23017_GPPUB, self.pullups >> 8)

        return self.pullups


    # Read value from single input pin
    def input(self, pin, check=True):

        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, must be between 0 and %s" % (pin, self.num_gpios-1)
        if check:
            assert (self.direction & (1 << pin)) != 0, "Pin %s not set to input" % pin

        if self.num_gpios <= 8:
            value = self.i2c.readU8(self.MCP23008_GPIO)
            return (value >> pin) & 1
        elif pin < 8:
            # Read from low bits (GPIOA)
            value = self.i2c.readU8(self.MCP23017_GPIOA)
            return (value >> pin) & 1
        else:
            # Read from high bits (GPIOB)
            value = self.i2c.readU8(self.MCP23017_GPIOB)
            return (value >> (pin - 8)) & 1


    # Write value to single output pin
    def output(self, pin, value):
        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, must be between 0 and %s" % (pin, self.num_gpios-1)
        # assert self.direction & (1 << pin) == 0, "Pin %s not set to output" % pin

        if value: new = self.outputvalue |  (1 << pin)
        else:     new = self.outputvalue & ~(1 << pin)

        # Only write if pin value has changed:
        if new is not self.outputvalue:
            self.outputvalue = new
            if self.num_gpios <= 8:
                self.i2c.write8(self.MCP23008_OLAT, new)
            elif pin < 8:
                # Write to low bits (OLATA)
                self.i2c.write8(self.MCP23017_OLATA, new & 0xFF)
            else:
                # Write to high bits (OLATB)
                self.i2c.write8(self.MCP23017_OLATB, new >> 8)

        return new


# The following two methods (inputAll and outputAll) neither assert
# inputs nor invoke the base class methods that handle I/O exceptions.
# The underlying smbus calls are invoked directly for expediency, the
# expectation being that any I2C access or address type errors have
# already been identified during initialization.

    # Read contiguous value from all input pins
    def inputAll(self):
      if self.num_gpios <= 8:
        return self.i2c.bus.read_byte_data(self.i2c.address,
         self.MCP23008_GPIO)
      else:
        return self.i2c.bus.read_word_data(self.i2c.address,
         self.MCP23017_GPIOA)


    # Write contiguous value to all output pins
    def outputAll(self, value):
      self.outputvalue = value
      if self.num_gpios <= 8:
        self.i2c.bus.write_byte_data(self.i2c.address,
         self.MCP23008_OLAT, value)
      else:
        self.i2c.bus.write_word_data(self.i2c.address,
         self.MCP23017_OLATA, value)


# RPi.GPIO compatible interface for MCP23017 and MCP23008

class MCP230XX_GPIO(object):
    OUT   = 0
    IN    = 1
    BCM   = 0
    BOARD = 0

    def __init__(self, busnum, address, num_gpios):
        self.chip = Adafruit_MCP230XX(busnum, address, num_gpios)
    def setmode(self, mode):
        pass # do nothing
    def setup(self, pin, mode):
        self.chip.config(pin, mode)
    def input(self, pin):
        return self.chip.input(pin)
    def output(self, pin, value):
        self.chip.output(pin, value)
    def pullup(self, pin, value):
        self.chip.pullup(pin, value)


if __name__ == '__main__':

    # ****************************************************
    # Set num_gpios to 8 for MCP23008 or 16 for MCP23017!
    # If you have a new Pi you may also need to add: bus=1
    # ****************************************************
    mcp = Adafruit_MCP230XX(address=0x20, num_gpios=16)
    
    # Set pins 0, 1, 2 as outputs
    mcp.config(0, mcp.OUTPUT)
    mcp.config(1, mcp.OUTPUT)
    mcp.config(2, mcp.OUTPUT)
    
    # Set pin 3 to input with the pullup resistor enabled
    mcp.pullup(3, True)

    # Read pin 3 and display the results
    print "%d: %x" % (3, mcp.input(3))
    
    # Python speed test on output 0 toggling at max speed
    while True:
      mcp.output(0, 1) # Pin 0 High
      mcp.output(0, 0) # Pin 0 Low
