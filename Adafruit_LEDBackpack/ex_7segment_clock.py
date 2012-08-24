#!/usr/bin/python

import time
import datetime
from Adafruit_7Segment import SevenSegment

# ===========================================================================
# Clock Example
# ===========================================================================
segment = SevenSegment(address=0x70)

print "Press CTRL+Z to exit"

# Continually update the time on a 4 char, 7-segment display
while(True):
  now = datetime.datetime.now()
  hour = now.hour
  minute = now.minute
  second = now.second
  # Set hours
  segment.writeDigit(0, int(hour / 10))     # Tens
  segment.writeDigit(1, hour % 10)          # Ones
  # Set minutes
  segment.writeDigit(3, int(minute / 10))   # Tens
  segment.writeDigit(4, minute % 10)        # Ones
  # Toggle color
  segment.setColon(second % 2)              # Toggle colon at 1Hz
  # Wait one second
  time.sleep(1)
