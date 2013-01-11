#!/usr/bin/python

from Adafruit_VCNL4000 import VCNL4000
import time

# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the VNCL4000 sensor
vcnl = VCNL4000(0x13)

# Print proximity sensor data every 100 ms
while True:
	
	print "Data from proximity sensor", vcnl.read_proximity()
	time.sleep(0.1)
