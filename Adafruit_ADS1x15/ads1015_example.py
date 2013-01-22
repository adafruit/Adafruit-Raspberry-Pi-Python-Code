#!/usr/bin/python

from Adafruit_ADS1x15 import ADS1x15

# ============================================================================
# Example Code
# ============================================================================
ADS1015 = 0x00	# 12-bit ADC
ADS1115 = 0x01	# 16-bit ADC

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ToDo: Change the value below depending on which chip you're using!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ADS_Current = ADS1115

# Initialise the ADC using the default mode (use default I2C address)
adc = ADS1x15(ic=ADS_Current)

# Read channel 0 in single-ended mode 
result = adc.readADCSingleEnded(0)
if ADS_Current == ADS1015:
  # For ADS1015 at max range (+/-6.144V) 1 bit = 3mV (12-bit values)
  print "Channel 0 = %.3f V" % (result * 0.003)
else:
  # For ADS1115 at max range (+/-6.144V) 1-bit = 0.1875mV (16-bit values)
  print "Channel 0 = %.3f V" % (result * 0.0001875)

# Read channel 1 in single-ended mode 
result = adc.readADCSingleEnded(1)
if ADS_Current == ADS1015:
  # For ADS1015 at max range (+/-6.144V) 1 bit = 3mV (12-bit values)
  print "Channel 1 = %.3f V" % (result * 0.003)
else:
  # For ADS1115 at max range (+/-6.144V) 1-bit = 0.1875mV (16-bit values)
  print "Channel 1 = %.3f V" % (result * 0.0001875)
