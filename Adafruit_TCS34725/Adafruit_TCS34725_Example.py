#!/usr/bin/python
from time import sleep
from Adafruit_TCS34725 import TCS34725

# ===========================================================================
# Example Code
# ===========================================================================

# Initialize the TCS34725 and use default integration time and gain
# tcs34725 = TCS34725(debug=True)
tcs = TCS34725(integrationTime=0xEB, gain=0x01)
tcs.setInterrupt(False)
sleep(1)

rgb = tcs.getRawData()
colorTemp = tcs.calculateColorTemperature(rgb)
lux = tcs.calculateLux(rgb)
print rgb
if colorTemp is None:
    print 'Too dark to determine color temperature!'
else:
    print "Color Temperature: %d K" % colorTemp
print "Luminosity: %d lux" % lux
tcs.setInterrupt(True)
sleep(1)
tcs.disable()
