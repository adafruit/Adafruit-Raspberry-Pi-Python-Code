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

## Where do I find the new Raspberry Pi Python code?

**All** of the Python libraries now support Python 3.x and a wide variety of Linux/Single Board Computers.

This library has been deprecated in favor of <a href="https://github.com/adafruit/Adafruit_Blinka">our python3 Blinka library</a>. We have replaced all of the libraries that use this repo with CircuitPython libraries that are Python3 compatible, and support a <a href="https://circuitpython.org/blinka" rel="nofollow">wide variety of single board/linux computers</a>!</p>
<p>Visit <a href="https://circuitpython.org/blinka" rel="nofollow">https://circuitpython.org/blinka</a> for more information</p>
<p>CircuitPython has <a href="https://circuitpython.readthedocs.io/projects/bundle/en/latest/drivers.html" rel="nofollow">support for almost 200 different drivers</a>, and a  as well as <a href="https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h" rel="nofollow">FT232H support for Mac/Win/Linux</a>!</p>

## But I **need** the old code!  What can I do?

Don't worry the old Adafruit Raspberry-Pi Python code can be found in the
[legacy branch](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/legacy) of this repository.  This is a snapshot of the old code before it
was refactored into individual libraries. **Note this legacy code will not be
maintained!**
