# Adafruit's Legacy Raspberry Pi Python Code Library

## What happened to all the Raspberry Pi Python code!?

In the past this repository held all of the Raspberry Pi related Python code
that Adafruit published.  For example code to talk to sensors like the BMP085,
TCS34725, and other hardware like character LCD plates.  Over time we found it
difficult to manage so much code in a single repository, and couldn't easily put
the code on Python's package index for simple installation.  Now we've broken out
all of the previous Python code into individual GitHub repositories, and we've
loaded all of these repositories on the [Python package index](https://pypi.python.org/pypi)
so they can be installed with `pip` (note that pip won't install example code so for most users
it's recommended to install from source).

In addition **all** of the Python libraries below support **both** Python 2.7 and Python 3.x!  Note
if you do plan to use Python 3 it has totally separate libraries from Python 2 so you might
need to install all the libraries you use in **both** Python 2 and 3.  See this video stream
for more details: https://www.youtube.com/watch?v=rRFG32EebNc  In particular on a Raspberry Pi
you probably want to install Python 3, PIP for Python 3, and the RPi.GPIO library (used
to talk to GPIO pins on the Pi) with these commands:

    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python-dev
    sudo pip3 install rpi.gpio

## Where do I find the new Raspberry Pi Python code?

Here is a table with each of the old libraries and a link to their new unique
GitHub repositories and easy pip install names:

| Old Library Name | New Library Location | New `pip install` Package Name | Notes |
|------------------|----------------------|--------------------------------|-------|
| Adafruit_ADS1x15 | https://github.com/adafruit/Adafruit_Python_ADS1X15 | adafruit-ads1x15 | [See guide](https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters). |
| Adafruit_ADXL345 | https://github.com/adafruit/Adafruit_Python_ADXL345 | adafriut-adxl345 | - |
| Adafruit_BMP085 | https://github.com/adafruit/Adafruit_Python_BMP | adafruit-bmp | [See guide](https://learn.adafruit.com/using-the-bmp085-with-raspberry-pi/using-the-adafruit-bmp085-python-library). |
| Adafruit_CharLCD | https://github.com/adafruit/Adafruit_Python_CharLCD | adafruit-charlcd | [See new character LCD guide](https://learn.adafruit.com/character-lcd-with-raspberry-pi-or-beaglebone-black/overview). |
| Adafruit_CharLCDPlate | https://github.com/adafruit/Adafruit_Python_CharLCD | adafruit-charlcd | [See new character LCD guide](https://learn.adafruit.com/character-lcd-with-raspberry-pi-or-beaglebone-black/overview). |
| Adafruit_DHT_Driver | https://github.com/adafruit/Adafruit_Python_DHT | None, must be manually installed to properly compile C extension. | See the [C code for reading the DHT sensor](https://github.com/adafruit/Adafruit_Python_DHT/tree/master/source/Raspberry_Pi_2) in the updated Python driver. |
| Adafruit_DHT_Driver_Python | https://github.com/adafruit/Adafruit_Python_DHT | None, must be manually installed to properly compile C extension. | [See updated DHT sensor guide](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/overview) |
| Adafruit_I2C | https://github.com/adafruit/Adafruit_Python_GPIO | adafruit-gpio | See [updated I2C code](https://github.com/adafruit/Adafruit_Python_GPIO/blob/master/Adafruit_GPIO/I2C.py) in the Python GPIO library.  Import with `import Adafruit_GPIO.I2C as I2C` and create an instance of `I2C.Device` instead of the old `Adafruit_I2C` class. |
| Adafruit_LEDBackpack | https://github.com/adafruit/Adafruit_Python_LED_Backpack | adafruit-led-backpack | [See new LED backpacks guide.](https://learn.adafruit.com/led-backpack-displays-on-raspberry-pi-and-beaglebone-black/overview) |
| Adafruit_LEDpixels | https://github.com/adafruit/Adafruit_Python_WS2801 | adafruit-ws2801 | - |
| Adafruit_LSM303 | https://github.com/adafruit/Adafruit_Python_LSM303 | adafruit-lsm303 | - |
| Adafruit_MCP230xx | https://github.com/adafruit/Adafruit_Python_GPIO | adafruit-gpio | See [updated MCP230xx code](https://github.com/adafruit/Adafruit_Python_GPIO/blob/master/Adafruit_GPIO/MCP230xx.py). |
| Adafruit_MCP3002 | Deprecated, see MCP3008 chip. | - | - |
| Adafruit_MCP3008 | https://github.com/adafruit/Adafruit_Python_MCP3008 | adafruit-mcp3008 | [See guide](https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters). |
| Adafruit_MCP4725 | https://github.com/adafruit/Adafruit_Python_MCP4725 | adafruit-mcp4725 | [See guide](https://learn.adafruit.com/mcp4725-12-bit-dac-with-raspberry-pi/overview) |
| Adafruit_PWM_Servo_Driver | https://github.com/adafruit/Adafruit_Python_PCA9685 | adafruit-pca9685 | [See guide](https://learn.adafruit.com/adafruit-16-channel-servo-driver-with-raspberry-pi/overview) |
| Adafruit_TCS34725 | https://github.com/adafruit/Adafruit_Python_TCS34725 | adafruit-tcs34725 | - |
| Adafruit_VCNL4000 | https://github.com/adafruit/Adafruit_Python_VCNL40xx | adafruit-vcnl40xx | - |

You might also be interested in other Python libraries which were never in this repository but are handy for talking
to other hardware:

| Device / Guide | Library Location | `pip install` Package Name |
|----------------|------------------|----------------------------|
| [BME280 Humidity & Pressure Sensor](https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout/overview) | https://github.com/adafruit/Adafruit_Python_BME280 | TBD |
| [BNO055 Absolute Orientation Sensor](https://learn.adafruit.com/bno055-absolute-orientation-sensor-with-raspberry-pi-and-beaglebone-black/overview) | https://github.com/adafruit/Adafruit_Python_BNO055 | adafruit-bno055 |
| [ILI9341 LCD Displays](https://learn.adafruit.com/user-space-spi-tft-python-library-ili9341-2-8/overview) | https://github.com/adafruit/Adafruit_Python_ILI9341 | adafruit-ili9341 |
| [MAX31855 Thermocouple Sensor](https://learn.adafruit.com/max31855-thermocouple-python-library/overview) | https://github.com/adafruit/Adafruit_Python_MAX31855 | adafruit-max31855 |
| [MAX9744 Class D Amplifier](https://learn.adafruit.com/adafruit-20w-stereo-audio-amplifier-class-d-max9744/overview) | https://github.com/adafruit/Adafruit_Python_MAX9744 | adafruit-max9744 |
| [MCP9808 Temperature Sensor](https://learn.adafruit.com/mcp9808-temperature-sensor-python-library/overview) | https://github.com/adafruit/Adafruit_Python_MCP9808 | adafruit-mcp9808 |
| [PN532 NFC Interface](https://learn.adafruit.com/raspberry-pi-nfc-minecraft-blocks/overview) | https://github.com/adafruit/Adafruit_Python_PN532 | adafruit-pn532 |
| [SSD1306 OLED Displays](https://learn.adafruit.com/ssd1306-oled-displays-with-raspberry-pi-and-beaglebone-black/overview) | https://github.com/adafruit/Adafruit_Python_SSD1306 | adafruit-ssd1306 |
| [TMP006 & TMP007 Temperature Sensors](https://learn.adafruit.com/tmp006-temperature-sensor-python-library/overview) | https://github.com/adafruit/Adafruit_Python_TMP | adafruit-tmp |

## But I **need** the old code!  What can I do?

Don't worry the old Adafruit Raspberry-Pi Python code can be found in the
[legacy branch](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/legacy) of this repository.  This is a snapshot of the old code before it
was refactored into individual libraries. **Note this legacy code will not be
maintained!**
