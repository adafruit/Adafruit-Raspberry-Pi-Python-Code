#!/usr/bin/python

import time, signal, sys
from Adafruit_ADS1x15 import ADS1x15

def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        print adc.getLastConversionResults()/1000.0
        adc.stopContinuousConversion()
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
# Print 'Press Ctrl+C to exit'

ADS1015 = 0x00	# 12-bit ADC
ADS1115 = 0x01	# 16-bit ADC

# Initialise the ADC using the default mode (use default I2C address)
# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
adc = ADS1x15(ic=ADS1115)

# start comparator on channel 2 with a thresholdHigh=200mV and low=100mV
# in traditional mode, non-latching, +/-1.024V and 250sps
adc.startSingleEndedComparator(2, 200, 100, pga=1024, sps=250, activeLow=True, traditionalMode=True, latching=False, numReadings=1)

while True:
		print adc.getLastConversionResults()/1000.0
		time.sleep(0.25)

#time.sleep(0.1)
