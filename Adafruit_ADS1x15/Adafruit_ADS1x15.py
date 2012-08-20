#!/usr/bin/python

import time
from Adafruit_I2C import Adafruit_I2C

# ===========================================================================
# ADS1x15 Class
# ===========================================================================

class ADS1x15:
  i2c = None

  # IC Identifiers
  __IC_ADS1015                      = 0x00
  __IC_ADS1115                      = 0x01

  # Pointer Register
  __ADS1015_REG_POINTER_MASK        = 0x03
  __ADS1015_REG_POINTER_CONVERT     = 0x00
  __ADS1015_REG_POINTER_CONFIG      = 0x01
  __ADS1015_REG_POINTER_LOWTHRESH   = 0x02
  __ADS1015_REG_POINTER_HITHRESH    = 0x03

  # Config Register
  __ADS1015_REG_CONFIG_OS_MASK      = 0x8000
  __ADS1015_REG_CONFIG_OS_SINGLE    = 0x8000  # Write: Set to start a single-conversion
  __ADS1015_REG_CONFIG_OS_BUSY      = 0x0000  # Read: Bit = 0 when conversion is in progress
  __ADS1015_REG_CONFIG_OS_NOTBUSY   = 0x8000  # Read: Bit = 1 when device is not performing a conversion

  __ADS1015_REG_CONFIG_MUX_MASK     = 0x7000
  __ADS1015_REG_CONFIG_MUX_DIFF_0_1 = 0x0000  # Differential P = AIN0, N = AIN1 (default)
  __ADS1015_REG_CONFIG_MUX_DIFF_0_3 = 0x1000  # Differential P = AIN0, N = AIN3
  __ADS1015_REG_CONFIG_MUX_DIFF_1_3 = 0x2000  # Differential P = AIN1, N = AIN3
  __ADS1015_REG_CONFIG_MUX_DIFF_2_3 = 0x3000  # Differential P = AIN2, N = AIN3
  __ADS1015_REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended AIN0
  __ADS1015_REG_CONFIG_MUX_SINGLE_1 = 0x5000  # Single-ended AIN1
  __ADS1015_REG_CONFIG_MUX_SINGLE_2 = 0x6000  # Single-ended AIN2
  __ADS1015_REG_CONFIG_MUX_SINGLE_3 = 0x7000  # Single-ended AIN3

  __ADS1015_REG_CONFIG_PGA_MASK     = 0x0E00
  __ADS1015_REG_CONFIG_PGA_6_144V   = 0x0000  # +/-6.144V range
  __ADS1015_REG_CONFIG_PGA_4_096V   = 0x0200  # +/-4.096V range
  __ADS1015_REG_CONFIG_PGA_2_048V   = 0x0400  # +/-2.048V range (default)
  __ADS1015_REG_CONFIG_PGA_1_024V   = 0x0600  # +/-1.024V range
  __ADS1015_REG_CONFIG_PGA_0_512V   = 0x0800  # +/-0.512V range
  __ADS1015_REG_CONFIG_PGA_0_256V   = 0x0A00  # +/-0.256V range

  __ADS1015_REG_CONFIG_MODE_MASK    = 0x0100
  __ADS1015_REG_CONFIG_MODE_CONTIN  = 0x0000  # Continuous conversion mode
  __ADS1015_REG_CONFIG_MODE_SINGLE  = 0x0100  # Power-down single-shot mode (default)

  __ADS1015_REG_CONFIG_DR_MASK      = 0x00E0  
  __ADS1015_REG_CONFIG_DR_128SPS    = 0x0000  # 128 samples per second
  __ADS1015_REG_CONFIG_DR_250SPS    = 0x0020  # 250 samples per second
  __ADS1015_REG_CONFIG_DR_490SPS    = 0x0040  # 490 samples per second
  __ADS1015_REG_CONFIG_DR_920SPS    = 0x0050  # 920 samples per second
  __ADS1015_REG_CONFIG_DR_1600SPS   = 0x0080  # 1600 samples per second (default)
  __ADS1015_REG_CONFIG_DR_2400SPS   = 0x00A0  # 2400 samples per second
  __ADS1015_REG_CONFIG_DR_3300SPS   = 0x00C0  # 3300 samples per second

  __ADS1015_REG_CONFIG_CMODE_MASK   = 0x0010
  __ADS1015_REG_CONFIG_CMODE_TRAD   = 0x0000  # Traditional comparator with hysteresis (default)
  __ADS1015_REG_CONFIG_CMODE_WINDOW = 0x0010  # Window comparator

  __ADS1015_REG_CONFIG_CPOL_MASK    = 0x0008
  __ADS1015_REG_CONFIG_CPOL_ACTVLOW = 0x0000  # ALERT/RDY pin is low when active (default)
  __ADS1015_REG_CONFIG_CPOL_ACTVHI  = 0x0008  # ALERT/RDY pin is high when active

  __ADS1015_REG_CONFIG_CLAT_MASK    = 0x0004  # Determines if ALERT/RDY pin latches once asserted
  __ADS1015_REG_CONFIG_CLAT_NONLAT  = 0x0000  # Non-latching comparator (default)
  __ADS1015_REG_CONFIG_CLAT_LATCH   = 0x0004  # Latching comparator

  __ADS1015_REG_CONFIG_CQUE_MASK    = 0x0003
  __ADS1015_REG_CONFIG_CQUE_1CONV   = 0x0000  # Assert ALERT/RDY after one conversions
  __ADS1015_REG_CONFIG_CQUE_2CONV   = 0x0001  # Assert ALERT/RDY after two conversions
  __ADS1015_REG_CONFIG_CQUE_4CONV   = 0x0002  # Assert ALERT/RDY after four conversions
  __ADS1015_REG_CONFIG_CQUE_NONE    = 0x0003  # Disable the comparator and put ALERT/RDY in high state (default)

  # Constructor
  def __init__(self, address=0x48, ic=__IC_ADS1015, debug=False):
    self.i2c = Adafruit_I2C(address)
    self.address = address
    self.debug = debug

    # Make sure the IC specified is valid
    if ((ic < self.__IC_ADS1015) | (ic > self.__IC_ADS1115)):
      if (self.debug):
        print "ADS1x15: Invalid IC. Using the ADS1015 by default"
      self.ic = __IC_ADS1015
    else:
      self.ic = ic

  def readADCSingleEnded(self, channel=0):
    "Gets a single-ended ADC reading from the specified channel (1 bit = 3mV)"
    # Default to channel 0 with invalid channel, or return -1?
    if (channel > 3):
      if (self.debug):
        print "ADS1x15: Invalid channel specified: %d" % channel
      return -1

    # Start with default values
    config = self.__ADS1015_REG_CONFIG_CQUE_NONE    | \
             self.__ADS1015_REG_CONFIG_CLAT_NONLAT  | \
             self.__ADS1015_REG_CONFIG_CPOL_ACTVLOW | \
             self.__ADS1015_REG_CONFIG_CMODE_TRAD   | \
             self.__ADS1015_REG_CONFIG_DR_1600SPS   | \
             self.__ADS1015_REG_CONFIG_MODE_SINGLE

    # Set PGA/voltage range (1 bit = 3mV using the default range)
    config |= self.__ADS1015_REG_CONFIG_PGA_6_144V    # +/- 6.144V range

    if channel == 3:
      config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_3
    elif channel == 2:
      config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_2
    elif channel == 1:
      config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_1
    else:
      config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_0

    # Set 'start single-conversion' bit
    config |= self.__ADS1015_REG_CONFIG_OS_SINGLE

    # Write config register to the ADC
    bytes = [(config >> 8) & 0xFF, config & 0xFF]
    self.i2c.writeList(self.__ADS1015_REG_POINTER_CONFIG, bytes)

    # Wait for the ADC conversion to complete
    time.sleep(0.001)

    # Read the conversion results
    result = self.i2c.readList(self.__ADS1015_REG_POINTER_CONVERT, 2)
    if (self.ic == self.__IC_ADS1015):
      # Shift right 4 bits for the 12-bit ADS1015
       return ( ((result[0] << 8) | (result[1] & 0xFF)) >> 4 )
    else:
      # Return 16-bit value for the ADS1115
      return ( (result[0] << 8) | (result[1] & 0xFF) )

  def readADCDifferential01(self):
    "Gets a differential ADC reading from channels 0 and 1"

  def readADCDifferential23(self):
    "Gets a differential ADC reading from channels 2 and 3"

  def startSingleEndedComparator(self, channel, threshold):
    "Starts the comparator in single-ended mode on the specified channel"

  def getLastConversionResults(self):
    "Returns the last ADC conversion result"

