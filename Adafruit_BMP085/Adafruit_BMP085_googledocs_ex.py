#!/usr/bin/python

import sys
import time
import datetime
import gspread
from Adafruit_BMP085 import BMP085

# ===========================================================================
# Google Account Details
# ===========================================================================

# Account details for google docs
email       = 'you@somewhere.com'
password    = '$hhh!'
spreadsheet = 'SpreadsheetName'

# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the BMP085 and use STANDARD mode (default value)
# bmp = BMP085(0x77, debug=True)
bmp = BMP085(0x77)

# To specify a different operating mode, uncomment one of the following:
# bmp = BMP085(0x77, 0)  # ULTRALOWPOWER Mode
# bmp = BMP085(0x77, 1)  # STANDARD Mode
# bmp = BMP085(0x77, 2)  # HIRES Mode
# bmp = BMP085(0x77, 3)  # ULTRAHIRES Mode

# Login with your Google account
try:
  gc = gspread.login(email, password)
except:
  print "Unable to log in.  Check your email address/password"
  sys.exit()

# Open a worksheet from your spreadsheet using the filename
try:
  worksheet = gc.open(spreadsheet).sheet1
  # Alternatively, open a spreadsheet using the spreadsheet's key
  # worksheet = gc.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')
except:
  print "Unable to open the spreadsheet.  Check your filename: %s" % spreadsheet
  sys.exit()

# Continuously append data
while(True):
  temp = bmp.readTemperature()
  pressure = bmp.readPressure()
  altitude = bmp.readAltitude()

  print "Temperature: %.2f C" % temp
  print "Pressure:    %.2f hPa" % (pressure / 100.0)
  print "Altitude:    %.2f" % altitude

  # Append the data in the spreadsheet, including a timestamp
  try:
    values = [datetime.datetime.now(), temp, pressure, altitude]
    worksheet.append_row(values)
  except:
    print "Unable to append data.  Check your connection?"
    sys.exit()

  # Wait 5 seconds before continuing
  print "Wrote a row to %s" % spreadsheet
  time.sleep(5)

