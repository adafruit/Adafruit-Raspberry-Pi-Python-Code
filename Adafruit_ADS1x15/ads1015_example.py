#!/usr/bin/python

from Adafruit_ADS1x15 import ADS1x15

# ============================================================================
# Example Code
# ============================================================================

# Initialise the ADC using the default mode (IC = ADS1015, default address)
adc = ADS1x15()

# Read channel 0 and 1 in single-ended mode (1 bit = 3mV)
result = adc.readADCSingleEnded(0)
print "Channel 0 = %.3f V" % ((result * 3.0) / 1000.0)

result = adc.readADCSingleEnded(1)
print "Channel 1 = %.3f V" % ((result * 3.0) / 1000.0)

