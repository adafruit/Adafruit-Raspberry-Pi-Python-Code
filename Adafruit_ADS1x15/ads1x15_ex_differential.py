#!/usr/bin/python

import time, signal, sys
from Adafruit_ADS1x15 import ADS1x15

def signal_handler(signal, frame):
        #print 'You pressed Ctrl+C!'
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
#print 'Press Ctrl+C to exit'

ADS1015 = 0x00	# 12-bit ADC
ADS1115 = 0x01	# 16-bit ADC

# Initialise the ADC using the default mode (use default I2C address)
# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
adc = ADS1x15(ic=ADS1115)

# Read channels 2 and 3 in single-ended mode, at +/-4.096V and 250sps
volts2 = adc.readADCSingleEnded(2, 4096, 250)/1000.0
volts3 = adc.readADCSingleEnded(3, 4096, 250)/1000.0

# Now do a differential reading of channels 2 and 3
voltsdiff = adc.readADCDifferential23(4096, 250)/1000.0

# Display the two different reading for comparison purposes
print "%.8f %.8f %.8f %.8f" % (volts2, volts3, volts3-volts2, -voltsdiff)
