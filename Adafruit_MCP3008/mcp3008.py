#!/usr/bin/env python

# just some bitbang code for testing all 8 channels

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

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
	if ((adcnum > 7) or (adcnum < 0)):
		return -1
	GPIO.output(cspin, True)

	GPIO.output(clockpin, False)  # start clock low
	GPIO.output(cspin, False)     # bring CS low

	commandout = adcnum
	commandout |= 0x18  # start bit + single-ended bit
	commandout <<= 3    # we only need to send 5 bits here
	for i in range(5):
		if (commandout & 0x80):
			GPIO.output(mosipin, True)
		else:
   			GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

	adcout = 0
	# read in one empty bit, one null bit and 10 ADC bits
	for i in range(12):
		GPIO.output(clockpin, True)
		GPIO.output(clockpin, False)
		adcout <<= 1
		if (GPIO.input(misopin)):
			adcout |= 0x1

	GPIO.output(cspin, True)

	adcout /= 2       # first bit is 'null' so drop it
	return adcout
	
if __name__=='__main__':

	try:
		# change these as desired
		SPICLK = 18
		SPIMISO = 21
		SPIMOSI = 17
		SPICS = 22

		# set up the SPI interface pins 
		GPIO.setup(SPICLK, GPIO.OUT)
		GPIO.setup(SPIMISO, GPIO.IN)
		GPIO.setup(SPIMOSI, GPIO.OUT)
		GPIO.setup(SPICS, GPIO.OUT)

		# Note that bitbanging SPI is incredibly slow on the Pi as its not
		# a RTOS - reading the ADC takes about 30 ms (~30 samples per second)
		# which is awful for a microcontroller but better-than-nothing for Linux

		print "| #0 \t #1 \t #2 \t #3 \t #4 \t #5 \t #6 \t #7\t|"
		print "-----------------------------------------------------------------"
		while True:
			print "|",
			for adcnum in range(8):
				ret = readadc(adcnum, SPICLK, SPIMOSI, SPIMISO, SPICS)
				print ret,"\t",
			print "|"
        
	except KeyboardInterrupt:
		pass

	GPIO.cleanup()
