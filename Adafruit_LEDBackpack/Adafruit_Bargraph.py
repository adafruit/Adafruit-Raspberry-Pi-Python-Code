#!/usr/bin/python

import time
import datetime
from Adafruit_LEDBackpack import LEDBackpack

# ===========================================================================
# Bargraph Display
# ===========================================================================

# This class is meant to be used with the 24-LED bicolor bargraph
# displays available from Adafruit

class Bargraph:
  disp = None
 
  LED_OFF = 0
  LED_RED = 1
  LED_GREEN = 2
  LED_YELLOW = 3

  # Constructor
  def __init__(self, address=0x70, debug=False):
    self.debug = debug

    if self.debug:
      print "Initializing a new instance of LEDBackpack at 0x%02X" % address
    self.disp = LEDBackpack(address=address, debug=debug)

  def setLed(self, bar, color):
    if bar > 24:
      return
    if color > 3:
      return

    if bar < 12:
      c = bar / 4
    else:
      c = (bar - 12) / 4

    a = bar % 4;
    if bar >= 12:
      a += 4;
    
    if self.debug:
      print "Ano = %d Cath %d" % (a, c)

    bufRow = self.disp.getBufferRow(c) & ~((1 << a) | (1 << (a+8))) # turn off the LED

    if color == self.LED_RED:
      self.disp.setBufferRow(c, bufRow | (1 << a))
    elif color == self.LED_YELLOW:
      self.disp.setBufferRow(c, bufRow | (1 << a) | (1 << (a+8)))
    elif color == self.LED_GREEN:
      self.disp.setBufferRow(c, bufRow | 1 << (a+8))
