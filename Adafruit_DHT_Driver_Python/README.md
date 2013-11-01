Build dependencies for dhtreader python library

* python-dev
* bcm2835 library: http://www.airspayce.com/mikem/bcm2835/

Run following command to build the library:
```
python setup.py build
```

After that you should be able to find a dhtreader.so file inside `build`
directory. Put that library file in the same directory with your Python script,
then you are good to go.

Usage example:

```python
import dhtreader

type = 22
pin = 24

dhtreader.init()
print dhtreader.read(type, pin)
```
