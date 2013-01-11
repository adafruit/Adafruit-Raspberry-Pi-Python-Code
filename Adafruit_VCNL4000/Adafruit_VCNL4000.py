#!/usr/bin/python

import time
from Adafruit_I2C import Adafruit_I2C

# ===========================================================================
# VCNL4000 Class
# ===========================================================================

# Address of the sensor
VCNL4000_ADDRESS = 0x13

# Commands
VCNL4000_COMMAND = 0x80
VCNL4000_PRODUCTID = 0x81
VCNL4000_IRLED = 0x83
VCNL4000_AMBIENTPARAMETER = 0x84
VCNL4000_AMBIENTDATA = 0x85
VCNL4000_PROXIMITYDATA = 0x87
VCNL4000_SIGNALFREQ = 0x89
VCNL4000_PROXINITYADJUST = 0x8A

VCNL4000_3M125 = 0
VCNL4000_1M5625 = 1
VCNL4000_781K25 = 2
VCNL4000_390K625 = 3

VCNL4000_MEASUREAMBIENT = 0x10
VCNL4000_MEASUREPROXIMITY = 0x08
VCNL4000_AMBIENTREADY = 0x40
VCNL4000_PROXIMITYREADY = 0x20

class VCNL4000 :
  i2c = None

  # Constructor
  def __init__(self, address=0x13):
    self.i2c = Adafruit_I2C(address)

    self.address = address

    # Write proximity adjustement register
    self.i2c.write8(VCNL4000_PROXINITYADJUST, 0x81);

  # Read data from proximity sensor
  def read_proximity(self):
    self.i2c.write8(VCNL4000_COMMAND, VCNL4000_MEASUREPROXIMITY)
    while True:
      result = self.i2c.readU8(VCNL4000_COMMAND)
      if (result and VCNL4000_PROXIMITYREADY):
        return self.i2c.readU16(VCNL4000_PROXIMITYDATA)
      time.sleep(0.001)


