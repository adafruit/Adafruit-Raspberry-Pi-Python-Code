#!/usr/bin/python

import time
import datetime
from Adafruit_Bargraph import Bargraph

# ===========================================================================
# Scroll through colors example
# ===========================================================================
bargraph = Bargraph(address=0x70)

print "Press CTRL+C to exit"

while(True):
  for color in range(1, 4):
    for i in range(24):
      print i
      bargraph.setLed(i, color)
      time.sleep(0.05)
