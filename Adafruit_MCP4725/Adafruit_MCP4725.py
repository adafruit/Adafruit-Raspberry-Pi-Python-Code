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
    if (voltage < 0):
      voltage = 0
    if (self.debug):
      print "Setting voltage to %04d" % voltage
    # Value needs to be left-shifted four bytes for the MCP4725
    bytes = [(voltage >> 4) & 0xFF, (voltage << 4) & 0xFF]
    if (persist):
      self.i2c.writeList(self.__REG_WRITEDACEEPROM, bytes)
    else:
      self.i2c.writeList(self.__REG_WRITEDAC, bytes)
