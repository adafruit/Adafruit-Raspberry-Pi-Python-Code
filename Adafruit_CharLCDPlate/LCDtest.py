#!/usr/bin/python

from time import sleep
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

# Initialize the LCD plate.  Should auto-detect correct I2C bus.  If not,
# pass '0' for early 256 MB Model B boards or '1' for all later versions
lcd = Adafruit_CharLCDPlate()

# Clear display and show greeting, pause 1 sec
lcd.clear()
lcd.message("Adafruit RGB LCD\nPlate w/Keypad!")
sleep(1)

# Cycle through backlight colors
col = (lcd.RED , lcd.YELLOW, lcd.GREEN, lcd.TEAL,
       lcd.BLUE, lcd.VIOLET, lcd.ON   , lcd.OFF)
for c in col:
    lcd.backlight(c)
    sleep(.5)

# Poll buttons, display message & set backlight accordingly
btn = ((lcd.LEFT  , 'Red Red Wine'              , lcd.RED),
       (lcd.UP    , 'Sita sings\nthe blues'     , lcd.BLUE),
       (lcd.DOWN  , 'I see fields\nof green'    , lcd.GREEN),
       (lcd.RIGHT , 'Purple mountain\nmajesties', lcd.VIOLET),
       (lcd.SELECT, ''                          , lcd.ON))
prev = -1
while True:
    for b in btn:
        if lcd.buttonPressed(b[0]):
            if b is not prev:
                lcd.clear()
                lcd.message(b[1])
                lcd.backlight(b[2])
                prev = b
            break
