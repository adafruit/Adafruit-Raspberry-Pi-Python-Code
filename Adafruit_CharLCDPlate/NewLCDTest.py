#!/usr/bin/python
# mod by bb 29 Jan 2013

from time import sleep
from random import randint
from Adafruit_I2C import Adafruit_I2C
from Adafruit_MCP230xx import Adafruit_MCP230XX
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
#from Adafruit_MCP230xx import MCP23017_GPIOB, MCP23017_IODIRB
MCP23017_IODIRA = 0x00
MCP23017_IODIRB = 0x01
MCP23017_GPIOA  = 0x12
MCP23017_GPIOB  = 0x13
MCP23017_GPPUA  = 0x0C
MCP23017_GPPUB  = 0x0D
MCP23017_OLATA  = 0x14
MCP23017_OLATB  = 0x15
import smbus


def binfill(num,len=8):
	return bin(num)[2:].zfill(len)
	
ReverseNib = [0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15]
	
def cur_right(num=1): # note num = 40 in 2 lines mode moves up/down to other line
	for cnt in range(num):
		lcd.mcp.write8(0x30, MCP23017_GPIOB) #RS=0, R/W=0, E=1, high nibble of lcd command reversed, 0. Going high sends this to LCD as hi bits of instruction code
		lcd.mcp.write8(0x04, MCP23017_GPIOB) #RS=0, R/W=0, E=0, low nibble of lcd command reversed, 0
		lcd.mcp.write8(0x24, MCP23017_GPIOB) #same with E=1 so going high sends this nibble to LCD as low bits of instruction code
		lcd.mcp.write8(0x04, MCP23017_GPIOB) #same as line two to send E low to finish 

def cur_left(num=1):
	for cnt in range(num):
		lcd.mcp.write8(0x30, MCP23017_GPIOB) #RS=0, R/W=0, E=1, high nibble of lcd command reversed, 0. Going high sends this to LCD as hi bits of instruction code
		lcd.mcp.write8(0x00, MCP23017_GPIOB) #RS=0, R/W=0, E=0, low nibble of lcd command reversed, 0
		lcd.mcp.write8(0x20, MCP23017_GPIOB) #same with E=1 so going high sends this nibble to LCD as low bits of instruction code
		lcd.mcp.write8(0x00, MCP23017_GPIOB) #same as line two to send E low to finish

def display_right(num=1): # note num = 40 in 2 lines mode moves up/down to other line
	for cnt in range(num):
		lcd.mcp.write8(0x30, MCP23017_GPIOB) #RS=0, R/W=0, E=1, high nibble of lcd command reversed, 0. Going high sends this to LCD as hi bits of instruction code
		lcd.mcp.write8(0x06, MCP23017_GPIOB) #RS=0, R/W=0, E=0, low nibble of lcd command reversed, 0
		lcd.mcp.write8(0x26, MCP23017_GPIOB) #same with E=1 so going high sends this nibble to LCD as low bits of instruction code
		lcd.mcp.write8(0x06, MCP23017_GPIOB) #same as line two to send E low to finish 

def cur_pos(num=0): 
# i.e. Set DDRAM address - the cursor will move to this address
# Note 
#   in two line mode DDRAM 0 to 39 is first line
#                    DDRAM 64 to 39+64 is second line
#   using num from 40 till 63 will set DDRAM to 64
#   using num from above 39+64 will set DDRAM to 0
#   in one line mode DDRAM goes from 0 to 79 and setting above will go to 0
	# make num become the instruction code for Set DDRAM address
	num &= 0x7f # truncate num to 7 bits
	num |= 0x80 # make highest bit 1
	# make first byte to send which contains the reverse high nibble of num
	hinum = (num & 0xf0) >> 4
	byte1 = 0x20 | (ReverseNib[hinum] << 1) # RS=0, R/W = 0, E = 1, high nibble of lcd command reversed, 0.
	lonum = (num & 0xf)
	byte2 = (ReverseNib[lonum] << 1) # RS=0, R/W = 0, E = 0, low nibble of lcd command reversed, 0.
	#print "num = ", bin8(num), "hinum = ", bin8(hinum), "lonum = ", bin8(lonum)
	#print "byte1 = ", bin8(byte1), "byte2 = ", bin8(byte2)
	lcd.mcp.write8(byte1, MCP23017_GPIOB) #Going high sends this to LCD as hi bits of instruction code
	lcd.mcp.write8(byte2, MCP23017_GPIOB) # E goes low
	lcd.mcp.write8(0x20 | byte2, MCP23017_GPIOB) # going high sends this nibble to LCD as low bits of instruction code
	lcd.mcp.write8(byte2, MCP23017_GPIOB) # send E low to finish  

def setCGRAMadd(num=0): 
# i.e. Set CGRAM address - Write/Read Data from RAM after this will use Character Graphic RAM
	# make num become the instruction code for Set CGRAM address
	num &= 0x3f # truncate num to 6 bits
	num |= 0x40 # make 2nd to highest bit 1
	# make first byte to send which contains the reverse high nibble of num
	hinum = (num & 0xf0) >> 4
	byte1 = 0x20 | (ReverseNib[hinum] << 1) # RS=0, R/W = 0, E = 1, high nibble of lcd command reversed, 0.
	lonum = (num & 0xf)
	byte2 = (ReverseNib[lonum] << 1) # RS=0, R/W = 0, E = 0, low nibble of lcd command reversed, 0.
	print "num = ", binfill(num), "hinum = ", binfill(hinum), "lonum = ", binfill(lonum)
	print "byte1 = ", binfill(byte1), "byte2 = ", binfill(byte2)
	lcd.mcp.write8(byte1, MCP23017_GPIOB) #Going high sends this to LCD as hi bits of instruction code
	lcd.mcp.write8(byte2, MCP23017_GPIOB) # E goes low
	lcd.mcp.write8(0x20 | byte2, MCP23017_GPIOB) # going high sends this nibble to LCD as low bits of instruction code
	lcd.mcp.write8(byte2, MCP23017_GPIOB) # send E low to finish  
	
def general_cmd(cmd,RS=0,RW=0,debug=0): 
# execute a general command for the LCD TC1602A-01T
# cmd are the 8 bits of instuction code from table pg. 11 
# if cmd is a read command (RW = 1) the value read is returned
	# make first byte to send which contains the reverse high nibble of cmd
	RSbit=0x80 if RS else 0x00
	RWbit=0x40 if RW else 0x00
	Ebit = 0x20
	hicmd = (cmd & 0xf0) >> 4
	byte1 = RSbit | RWbit | Ebit  | (ReverseNib[hicmd] << 1) # RS,RW, E = 1, high nibble of lcd command reversed, 0.
	locmd = (cmd & 0xf)
	byte2 = RSbit | RWbit | (ReverseNib[locmd] << 1) # RS,RW, E = 0, low nibble of lcd command reversed, 0.
	if debug:
		print "cmd = ", binfill(cmd), "hinum = ", binfill(hicmd), "locmd = ", binfill(locmd)
		print "byte1 = ", binfill(byte1), "byte2 = ", binfill(byte2)
	lcd.mcp.write8(byte1, MCP23017_GPIOB) #Going high sends this to LCD as hi bits of instruction code
	if RW:
		currentiodir = lcd.mcp.readU8(MCP23017_IODIRB) # save entering state of input/output for pins from 8-15
		lcd.mcp.write8(0b00011110 | currentiodir,  MCP23017_IODIRB) # configure input for pins 9-12 which are 4-7 in GPB
		num = lcd.mcp.readU8(MCP23017_GPIOB) # get input which will contain reversed high nibble from LCD
		hinum = ReverseNib[(num & 0b00011110) >> 1]    # extract the 4 bits and reverse
	lcd.mcp.write8(byte2, MCP23017_GPIOB) # E goes low
	lcd.mcp.write8(Ebit | byte2, MCP23017_GPIOB) # going high sends this nibble to LCD as low bits of instruction code
	if RW:
		num = lcd.mcp.readU8(MCP23017_GPIOB) # get input which will contain reversed low nibble from LCD
		lonum = ReverseNib[(num & 0b00011110) >> 1]   # extract the 4 bits and reverse
	if RW:
		lcd.mcp.write8(currentiodir,  MCP23017_IODIRB) # restore pins input/output to state upon entering this routine
	lcd.mcp.write8(0x00, MCP23017_GPIOB) # send all  low to finish and be compatible with other CarLCDPlate routines
	if RW:
		return (hinum << 4) | lonum	
	
def readfast(ram=False): 
# read BF and AC or RAM Data
	if ram:
		cmdhi = 0xe0
		cmdlo = 0xc0
	else:
		cmdhi = 0x60
		cmdlo = 0x40
	lcd.mcp.write8(0b00011111,  MCP23017_IODIRB) # configure so input on pins 9-12 which are 4-7 in GPB
	lcd.mcp.write8(cmdhi, MCP23017_GPIOB) #Going high prepares to record first nibble info
	num = lcd.mcp.readU8(MCP23017_GPIOB) # get input which will contain reversed high nibble from LCD
	hinum = ReverseNib[(num & 0b00011110) >> 1]    # extract the 4 bits and reverse# extract the 4 bits and reverse
	lcd.mcp.write8(cmdlo, MCP23017_GPIOB) # E goes low
	lcd.mcp.write8(cmdhi, MCP23017_GPIOB) # going high prepares to recond second nibble info
	num = lcd.mcp.readU8(MCP23017_GPIOB) # get input which will contain reversed low nibble from LCD
	lonum = ReverseNib[(num & 0b00011110) >> 1]    # extract the 4 bits and reverse
	lcd.mcp.write8(0x0, MCP23017_GPIOB) # send E low to finish  and set RS, RW and all to zero
	lcd.mcp.write8(0b00000001,  MCP23017_IODIRB) # configure so all approrpriate pins are output again	
	return (hinum << 4) | lonum

def DumpMCP23017Regs(regs_to_use=[0x0,18,20]):
# Dump MCP23017 registers see MCP2301721952b.pdf specifications but show first B then A
#  Default is to dump only IODIR, GPIO and OLATA
#  will show B bank followed by A bank i.e. IODIRB, IODIRA so
#  the output corresponds to 'pins' 15,14,...,0
#  to dump all use regs_to_use = range(0x0,0x15,0x2)
	RegName = ["IODIR","IPOL","GPINTEN","DEFVAL","INTCON","IOCON","GPPU","INTF","INTCAP","GPIO","OLATA"]
	print "B bank then A bank so Pins 15, 14, ..., 0"
	print binfill(lcd.mcp.direction,16), "  lcd.mcp.direction"  #ideally should be same as IODIR
	for reg in regs_to_use:
		str =  binfill(lcd.mcp.readU16(reg),16)
		# interchange bytes B reg then A reg so 'pins' are from left to right are 15,14,13,...,0
		print str[8:]+str[:8]," ", RegName[reg/2] 

def home_fast():		
# fast return home 
	lcd.mcp.write8(0x20, MCP23017_GPIOB) #same with E=1 so going high sends this nibble to LCD as hi bits of instruction code
	lcd.mcp.write8(0x08, MCP23017_GPIOB) #RS=0, R/W=0, E=0, low nibble of lcd command reversed, 0
	lcd.mcp.write8(0x28, MCP23017_GPIOB) #same with E=1 so going high sends this nibble to LCD as low bits of instruction code
	lcd.mcp.write8(0x08, MCP23017_GPIOB) #same as line three to send E low to finish  
    
def clear_fast():
# fast clear 
	lcd.mcp.write8(0x20, MCP23017_GPIOB) #same with E=1 so going high sends this nibble to LCD as hi bits of instruction code
	lcd.mcp.write8(0x10, MCP23017_GPIOB) #RS=0, R/W=0, E=0, low nibble of clear display reversed, 0
	lcd.mcp.write8(0x30, MCP23017_GPIOB) #same with E=1 so going high sends this nibble to LCD as low bits of instruction code
	lcd.mcp.write8(0x10, MCP23017_GPIOB) #same as line three to send E low to finish  
                
def dim_light(on=.5,time=1,nforsec=50):
# dimming routine doesnt work very well
# flashes display on and off over interval time
# on is fraction of time on during the interval
	assert 0 <= on and on <= 1, "bad value for on"
	ontime = float(on)/nforsec
	offtime = (1.0-on)/nforsec
	maxct = int(nforsec*time)
	print ontime, offtime, maxct
	for ct in range(maxct): 
		lcd.write4bits(0x8)   # display off
		sleep(offtime)
		lcd.write4bits(0xc)   # display on
		sleep(ontime)
		
def dispall(delay=.1):
	for i in range(256):
		general_cmd(i,1)
		sleep(delay)
		
def cycle(seq, n):
# cyclic premutation of seq shifting left n
    n = n % len(seq)
    return seq[n:] + seq[:n]
		
def cyclerange(DDRAMrange=range(40), amount=1):
# cyclically shift characters in a range of DDRAM addresses by amount
# DDRAMrange default is line 1 in 2 line mode i.e. 0...39
	# get DDRAM address to be restored
	add = general_cmd(0,0,1)
	lenrange = len(DDRAMrange)
	startadd = DDRAMrange[0]
	# get data in DDRAMrange
	# set DDRAM address to startadd
	general_cmd(0b10000000 + startadd)
	win = [0]*lenrange
	for i in range(lenrange): #read DDRAM beginning at startadd
		win[i] = general_cmd(0,1,1)
	win = cycle(win,amount)
	general_cmd(0b10000000 + startadd)
	for i in range(lenrange): #write shifted values back in DDRAM starting at startadd
		general_cmd(win[i],1,0)
	# restore DDRAM address
	general_cmd(add | 0x80)

def scrollrange(DDRAMrange=range(40), num=1, delay=.01):	
	num = num*len(DDRAMrange)
	for i in range(num):
		cyclerange(DDRAMrange,1)
		#sleep(delay)
	
def shiftwithinrange(textstart,textlen,DDRAMrange=range(40)):
# cyclically shift characters in a range of DDRAM addresses by one position
# this code maybe faster than cyclerange code
# DDRAMrange default is line 1 in 2 line mode i.e. 0...39
	# if have string of text can shift it to the right one place within a range (say top line)
	# assuming this string is surrounded by blanks in the rest of the range
	# assuming LCD set in increment mode (rather than decrement mode)
	# get DDRAM address to be restored
	add = general_cmd(0,0,1)
	startrange = DDRAMrange[0]
	endrange = DDRAMrange[-1]
	lenrange = len(DDRAMrange)
	#print startrange, endrange, lenrange
	for i in range(textstart+textlen-1,textstart-1,-1): # go thru in reverse
		add = i
		if i > endrange:
			add = i - lenrange + startrange
		#print "moving from ", add
		# set DDRAM address to 
		general_cmd(0b10000000 + add) 
		byte = general_cmd(0,1,1) # this will get byte in DDRAM and increment address counter by 1
		if i+1 > endrange:
			add = i + 1 - lenrange + startrange
			general_cmd(0b10000000 + add ) 
		else:
			add = add + 1		
		general_cmd(byte,1,0) # this will put byte in DDRAM at the new address thus shifting it
		#print "moving to ", add, "this char ",  chr(byte)
	general_cmd(0b10000000 + textstart) 
	general_cmd(0b00100000,1,0) # this will put blank 
	# restore DDRAM address
	general_cmd(add | 0x80)
	

class Histogram:	
	def __init__(self):
		# make bars in CGRAM of height 8 to 1 in for custom char 0 to 7 (and 8 to 15) 
		histdata = [31,31,31,31,31,31,31,31,  0,31,31,31,31,31,31,31,  0,0,31,31,31,31,31,31,  0,0,0,31,31,31,31,31,  0,0,0,0,31,31,31,31,  0,0,0,0,0,31,31,31,  0,0,0,0,0,0,31,31,  0,0,0,0,0,0,0,31  ]
		general_cmd(0b01000000) # set CGRAM address 0
		for i in range(64):
			general_cmd(histdata[i],1) # write data to ram

	def histogram(self,bar,DDRAMstart=64,UseTwoLines=True):
	# draws bars of height bar[0],bar[1],... starting at
	# DDRAMstart. Heights must >=0 and <= max 16 for TwoLines and 8 for OneLine).
	# In the case UseTwoLines==True, the bars use two rows, so it is advised
	# to make DDRAMstart on the 2nd line. 
	# note no checking done on values. If they are bigger than 16 other characters
	#   will be displayed instead of the custom bars. 
		# get DDRAM address to be restored
		add = general_cmd(0,0,1)
		# draw bottom row
		# set DDRAM address to start
		general_cmd(0b10000000 + DDRAMstart)
		for y in bar:
			char = max(16-y,8)
			general_cmd(char,1,0) # put char which has appropriate height
		if UseTwoLines:
			# draw top row
			# set DDRAM address to start
			general_cmd(0b10000000 + DDRAMstart - 64)
			for y in bar:
				char = min(16-y,8) + 8
				general_cmd(char,1,0) # put char which has appropriate height
		# restore DDRAM address
		general_cmd(add | 0x80)


class DotGrid:	
	def __init__(self):
		# make dot patterns in CGRAM  
		self.dotdata = [0,0,0,0,14,31,14,0,  14,31,14,0,0,0,0,0,  14,31,14,0,14,31,14,0,  0,0,0,0,0,14,31,14,  0,14,31,14,0,0,0,0,  0,14,31,14,0,14,31,14]
		self.dedata = [[[64,2,1,0],[64,2,0,1],[0,5,4,3],[0,5,3,4]], [[64,1,2,32],[64,0,2,32],[0,4,5,32],[0,3,5,32]]]
		self.isdotdata = [[64,0,2],[64,1,2],[0,3,5],[0,4,5]]
		self.initialize_CGRAM()
		
	def initialize_CGRAM(self):
		general_cmd(0b01000000) # set CGRAM address 0
		for i in range(len(self.dotdata)):
			general_cmd(self.dotdata[i],1) # write data to ram

	def draw_erase_or_test(self,x,y,deort):     # deort == 0 for draw, ==1 for erase, else test only
	# draws, erases or tests a dot at (x,y)
	# 0<=x<=39 but only x<=15 visable in default display but can shift to see
	# 0<=y<=3
		# get DDRAM address to be restored
		add = general_cmd(0,0,1)
		addforx = x	+ self.dedata[0][y][0]
		general_cmd(0b10000000 + addforx)    # set DDRAM address 
		byte = general_cmd(0,1,1) # this will get byte in DDRAM
		isdot = byte==self.isdotdata[y][1] or byte==self.isdotdata[y][2]
		# if asked to draw a dot thats not there or erase a dot that is there do it!
		if deort==0 and not isdot or deort==1 and isdot:   
			char = self.dedata[deort][y][1] if byte==self.dedata[deort][y][2] else self.dedata[deort][y][3] 
			general_cmd(0b10000000 + addforx)    # set DDRAM address 
			general_cmd(char,1,0) # put char which is one or two dots
		# restore DDRAM address
		general_cmd(add | 0x80)
		# return True if there was a dot at x,y when entered function
		return isdot
		
	def draw(self,x,y):
		return self.draw_erase_or_test(x,y,0)

	def erase(self,x,y):
 		return self.draw_erase_or_test(x,y,1)

	def isdot(self,x,y):	
		return self.draw_erase_or_test(x,y,2)


# OLD
#	def draw(self,x,y):
#	# draws a dot at (x,y)
#	# 0<=x<=39 but only x<=15 in default display can shift to see
#	# 0<=y<=3
#		# get DDRAM address to be restored
#		add = general_cmd(0,0,1)
#		if y==0:
#			addforx = x	+ 64
#			general_cmd(0b10000000 + addforx)    # set DDRAM address 
#			byte = general_cmd(0,1,1) # this will get byte in DDRAM 
#			char = 2 if byte==1 else 0 
#			general_cmd(0b10000000 + addforx)    # set DDRAM address 
#			general_cmd(char,1,0) # put char which is one or two dots
#		elif y==1:
#			addforx = 64 + x			
#			general_cmd(0b10000000 + addforx)    # set DDRAM address 
#			byte = general_cmd(0,1,1) # this will get byte in DDRAM 
#			char = 2 if byte==0 else 1 
#			general_cmd(0b10000000 + addforx)    # set DDRAM address 
#			general_cmd(char,1,0) # put char which is one or two dots
#		elif y==2:
#			addforx = x			
#			general_cmd(0b10000000 + addforx)    # set DDRAM address 
#			byte = general_cmd(0,1,1) # this will get byte in DDRAM 
#			char = 5 if byte==4 else 3 
#			general_cmd(0b10000000 + addforx)    # set DDRAM address 
#			general_cmd(char,1,0) # put char which is one or two dots
#		elif y==3:
#			addforx = x			
#			general_cmd(0b10000000 + addforx)    # set DDRAM address 
#			byte = general_cmd(0,1,1) # this will get byte in DDRAM 
#			general_cmd(0b10000000 + addforx)    # set DDRAM address 
#			general_cmd(char,1,0) # put char which is one or two dots			
#		else:
#			print "y not 0,1,2 or 3"
#		# restore DDRAM address
#		general_cmd(add | 0x80)
#			


back = 0
def ToggleBacklight(back):
	back ^= 1
	lcd.backlight(back)
	sleep(.2)
	return back



# initialize the LCD plate
# use busnum = 0 for raspi version 1 (256MB) and busnum = 1 for version 2
lcd = Adafruit_CharLCDPlate(busnum = 1)

Hist = Histogram()
bar = [0]*16

DotG = DotGrid()

general_cmd(0b1) # clear
lcd.waitBFlow()   # must wait for clear  to complete

# Testing using keyboard
while 1:
	cmd = raw_input()
	if cmd == 'help':
		print "10, 9, bf, cgram, config, cyclerange, dim,  dispall, dot, dotinit, dump, edot, histogram, histograminit, longchar, mess, oneline, ramdata, sdr, scrollrange, shiftwithinrange, test, twoline, quit"
		
	if cmd == 'test':
		print "Routine for testing"

	if cmd == '10':
		str = raw_input("10 bits of instruction code:")
		RS = str[0]=="1" # 1 is true
		RW = str[1]=="1" # 1 is true
		str = str[2:].zfill(8)
		num = int('0b'+str,2)
		numrpt = raw_input("repeat #:")
		numrpt = 1 if numrpt=="" else int(numrpt)
		for count in range(0,numrpt):
			print(general_cmd(num,RS,RW))
			
	if cmd == 'dim':
		time = 2
		on = input("Fraction on? ")
		nforsec = input("nforsec? ")
		dim_light(on,time,nforsec)	
			
	if cmd == 'bf':	
		#print "BF", lcd.readBF()
		print "fast BF + AD = ", binfill(readfast()) # read Busy Flag and Adress
		#print "BF + AD = ", lcd.read4bits() # read Busy Flag and Adress

	if cmd == 'sdr':
		numrpt = raw_input("Shift Display Right by ")
		numrpt = 1 if numrpt=="" else int(numrpt)
		display_right(numrpt) 
		
	if cmd == 'cyclerange':
		line = input("Window Range? ")
		line = range(40) if line=="" else line
		amt = raw_input("How much? ")
		amt = 1 if amt=="" else int(amt)
		cyclerange(line,amt)
		
	if cmd == 'dotinit':
		DotG.initialize_CGRAM()
		
	if cmd == 'dot':
		x = input("x? ")
		y = input("y? ")
		#print(DotG.draw_erase_or_test(x,y,0))
		print(DotG.draw(x,y))

	if cmd == 'edot':
		x = input("x? ")
		y = input("y? ")
		#print(DotG.draw_erase_or_test(x,y,1))
		print(DotG.erase(x,y))

	if cmd == 'histograminit':
		Hist.__init__()
		
	if cmd == 'histogram':
		#bar = input("Bar list? ")
		barcurrent = [0]*16
		barnew = barcurrent[:]
		barshow = barcurrent[:]
		for cnt in range(30):
			for ind in range(len(barcurrent)):
				barnew[ind] = randint(0,16)
			tmax = 4
			for time in range(tmax+1):
				for ind in range(len(barcurrent)):
					barshow[ind] = int(((tmax-time)*barcurrent[ind] + time*barnew[ind])/float(tmax))
				Hist.histogram(barshow)
			barcurrent = barnew[:]
		
	if cmd == 'scrollrange':
		line = input("Window Range? ")
		line = range(40) if line=="" else line
		scrollrange(line)
		
	if cmd == 'shiftwithinrange':
		#textstart = input('Start? ')
		#textlen = input('Length? ')
		#shiftwithinrange(textstart,textlen, range(10))
		#general_cmd(0b00011000) # display shift left
		for i in range(40):
			shiftwithinrange(i,16)
			general_cmd(0b00011000) # display shift left
			sleep(.05)
			
	if cmd == 'cgram':
		num = raw_input("CGRAM address? ")
		setCGRAMadd(int(num))

	if cmd == 'ramdata':
		print "fast RAM Data = ", binfill(readfast(True)) # read data from RAM
		#print "RAM Data = ", lcd.read4bits(True) # read data from RAM

	if cmd == 'mess':
		str = raw_input("message:")
		lcd.message(str);

	if cmd == '9':
		str = raw_input("9 bits of instruction code:")
		char_mode = str[0]=="1" # 1 is true
		str = str[1:].zfill(8)
		bits = int('0b'+str,2)
		print char_mode, str, bits
		numrpt = raw_input("repeat #:")
		numrpt = 1 if numrpt=="" else int(numrpt)
		for count in range(0,numrpt):
			lcd.write4bits(bits, char_mode)
			
	if cmd == 'dump':
		DumpMCP23017Regs()
		
	if cmd == 'config':
		pin = int(raw_input("pin number "))
		state = int(raw_input("1 or 0 "))==1
		lcd.mcp.config(pin,state)
		
	if cmd == 'oneline':
		general_cmd(0b100000)
		
	if cmd == 'twoline':
		general_cmd(0b101000)

	if cmd == 'longchar':
		general_cmd(0b100100)
		
	if cmd == 'dispall':
		dispall()

	if cmd == 'quit':
		exit()
		
# Testing using buttons on LCDPlate
while 1:
	if (lcd.buttonPressed(lcd.LEFT)):
		#print "BF", lcd.readBF()
		print "fast BF + AD = ", binfill(readfast()) # read Busy Flag and Adress
		#print "BF + AD = ", lcd.read4bits() # read Busy Flag and Adress
		#back = ToggleBacklight(back)
		sleep(.2)

	if (lcd.buttonPressed(lcd.UP)):
		num = raw_input("Shift Display Right by ")
		display_right(int(num)) 
		#num = raw_input("CGRAM address? ")
		#setCGRAMadd(int(num))
		sleep(.2) #prevent multiple execution while button is down

	if (lcd.buttonPressed(lcd.DOWN)):
		print "fast RAM Data = ", binfill(readfast(True)) # read data from RAM
		#print "RAM Data = ", lcd.read4bits(True) # read data from RAM
		sleep(.2)

	if (lcd.buttonPressed(lcd.RIGHT)):
		str = raw_input("message:")
		lcd.message(str);

	if (lcd.buttonPressed(lcd.SELECT)):
		str = raw_input("9 bits of instruction code:")
		char_mode = str[0]=="1" # 1 is true
		str = str[1:].zfill(8)
		bits = int('0b'+str,2)
		print char_mode, str, bits
		numrpt = raw_input("repeat #:")
		#print "input",numrpt
		if (numrpt == ""): # return means 1
			numrpt = 1
		else:
			numrpt = int(numrpt)
		for count in range(0,numrpt):
			lcd.write4bits(bits, char_mode)
