#!/usr/bin/python

from Adafruit_I2C import Adafruit_I2C

# ============================================================================
# Adafruit MCP4725 12-Bit DAC
# ============================================================================

class MCP4725 :
  i2c = None
  
  # Registers
  __REG_WRITEDAC         = 0x40
  __REG_WRITEDACEEPROM   = 0x60

  # Constructor
  def __init__(self, address=0x62, debug=False):
    self.i2c = Adafruit_I2C(address)
    self.address = address
    self.debug = debug

  def setVoltage(self, voltage, persist=False):
    "Sets the output voltage to the specified value"
    if (voltage > 4095):
      voltage = 4095
    if (self.debug):
      print "Setting voltage to %04d" % voltage
    # Value needs to be left-shifted four bytes for the MCP4725
    voltage <<= 4
    if (persist==True):
      self.i2c.write16(self.__REG_WRITEDACEEPROM, self.i2c.reverseByteOrder(voltage))
    else:
      self.i2c.write16(self.__REG_WRITEDAC, self.i2c.reverseByteOrder(voltage))

# Initialise a new instance of MCP4725 using the default address (0x62)
dac = MCP4725(0x62)
# Set output voltage to 50% VCC
dac.setVoltage(2048)
