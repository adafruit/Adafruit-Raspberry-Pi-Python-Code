#!/usr/bin/env python

# just some bitbang code for testing both channels

import RPi.GPIO as GPIO, time, os

DEBUG = 1
GPIO.setmode(GPIO.BCM)

# this function is not used, its for future reference!
def slowspiwrite(clockpin, datapin, byteout):
	GPIO.setup(clockpin, GPIO.OUT)
	GPIO.setup(datapin, GPIO.OUT)
	for i in range(8):
		if (byteout & 0x80):
			GPIO.output(datapin, True)
		else:
			GPIO.output(datapin, False)
		byteout <<= 1
		GPIO.output(clockpin, True)
		GPIO.output(clockpin, False)

# this function is not used, its for future reference!
def slowspiread(clockpin, datapin):
	GPIO.setup(clockpin, GPIO.OUT)
	GPIO.setup(datapin, GPIO.IN)
	byteout = 0
	for i in range(8):
		GPIO.output(clockpin, False)
		GPIO.output(clockpin, True)
		byteout <<= 1
		if (GPIO.input(datapin)):
			byteout = byteout | 0x1
	return byteout

# read SPI data from MCP3002 chip, 2 possible adc's (0 thru 1)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if ((adcnum > 1) or (adcnum < 0)):
        return -1
    GPIO.output(cspin, True)
    
    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low
    
    commandout = adcnum << 1;
    commandout |= 0x0D  # start bit + single-ended bit + MSBF bit
    commandout <<= 4    # we only need to send 4 bits here
    
    for i in range(4):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
    
    adcout = 0
    
    # read in one null bit and 10 ADC bits
    for i in range(11):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1
    GPIO.output(cspin, True)
    
    adcout /= 2       # first bit is 'null' so drop it
    return adcout
# change these as desired
SPICLK = 18
SPIMOSI = 17
SPIMISO = 21
SPICS = 22

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# Note that bitbanging SPI is incredibly slow on the Pi as its not
# a RTOS - reading the ADC takes about 30 ms (~30 samples per second)
# which is awful for a microcontroller but better-than-nothing for Linux

print "| #0 \t #1|"
print "-----------------------------------------------------------------"
while True:
	print "|",
	for adcnum in range(2):
		ret = readadc(adcnum, SPICLK, SPIMOSI, SPIMISO, SPICS)
		print ret,"\t",
	print "|"
