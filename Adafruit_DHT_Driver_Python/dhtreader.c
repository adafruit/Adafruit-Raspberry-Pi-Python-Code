/*  Python module for DHT temperature/humidity sensors
 *
 *  Modified by Qingping Hou from DHT reader example, original header:
 *
 *  How to access GPIO registers from C-code on the Raspberry-Pi
 *  Example program
 *  15-January-2012
 *  Dom and Gert
 */


/* for usleep */
#define _BSD_SOURCE

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <fcntl.h>
#include <assert.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <bcm2835.h>
#include <unistd.h>

#include <Python.h>

#define MAXTIMINGS 100

//#define DEBUG

#define DHT11 11
#define DHT22 22
#define AM2302 22

int readDHT(int type, int pin, float *temp_p, float *hum_p)
{
	int counter = 0;
	int laststate = HIGH;
	int i = 0;
	int j = 0;
	int checksum = 0;
#ifdef DEBUG
	int bitidx = 0;
	int bits[250];
#endif
	int data[100];

	// Set GPIO pin to output
	bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_OUTP);

	bcm2835_gpio_write(pin, HIGH);
	usleep(500000);  // 500 ms
	bcm2835_gpio_write(pin, LOW);
	usleep(20000);

	bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_INPT);

	data[0] = data[1] = data[2] = data[3] = data[4] = 0;

	// wait for pin to drop?
	while (bcm2835_gpio_lev(pin) == 1) {
		usleep(1);
	}

	// read data!
	for (i = 0; i < MAXTIMINGS; i++) {
		counter = 0;
		while ( bcm2835_gpio_lev(pin) == laststate) {
			counter++;
			//nanosleep(1);		// overclocking might change this?
			if (counter == 1000)
				break;
		}
		laststate = bcm2835_gpio_lev(pin);
		if (counter == 1000) break;
#ifdef DEBUG
		bits[bitidx++] = counter;
#endif

		if ((i>3) && (i%2 == 0)) {
			// shove each bit into the storage bytes
			data[j/8] <<= 1;
			if (counter > 200)
				data[j/8] |= 1;
			j++;
		}
	}

#ifdef DEBUG
	for (int i=3; i<bitidx; i+=2) {
		printf("bit %d: %d\n", i-3, bits[i]);
		printf("bit %d: %d (%d)\n", i-2, bits[i+1], bits[i+1] > 200);
	}
	printf("Data (%d): 0x%x 0x%x 0x%x 0x%x 0x%x\n", j, data[0], data[1], data[2], data[3], data[4]);
#endif

	if (j >= 39) {
		checksum = (data[0] + data[1] + data[2] + data[3]) & 0xFF;
		if (data[4] == checksum) {
			/* yay! checksum is valid */
			if (type == DHT11) {
				/*printf("Temp = %d *C, Hum = %d \%\n", data[2], data[0]);*/
				*temp_p = (float)data[2];
				*hum_p = (float)data[0];
			} else if (type == DHT22) {
				*hum_p = data[0] * 256 + data[1];
				*hum_p /= 10;

				*temp_p = (data[2] & 0x7F)* 256 + data[3];
				*temp_p /= 10.0;
				if (data[2] & 0x80)
					*temp_p *= -1;
				/*printf("Temp =  %.1f *C, Hum = %.1f \%\n", f, h);*/
			}
			return 0;
		}
		return -2;
	}

	return -1;
}


static PyObject *
dhtreader_init(PyObject *self, PyObject *args)
{
	return Py_BuildValue("i", bcm2835_init());
}

static PyObject *
dhtreader_read(PyObject *self, PyObject *args)
{
	int type, dhtpin;

	if (!PyArg_ParseTuple(args, "ii", &type, &dhtpin))
		return NULL;

	float t, h;
	int re = readDHT(type, dhtpin, &t, &h);

	if (re == 0) {
		return Py_BuildValue("(d,d)", t, h);
	} else if (re == -1) {
#ifdef DEBUG
		printf("sensor read failed! not enough data received\n");
#endif
	} else if (re == -2) {
#ifdef DEBUG
		printf("sensor read failed! checksum failed!\n");
#endif
	}

	return Py_BuildValue("");
}


static PyMethodDef DHTReaderMethods[] = {
	{"init", dhtreader_init, METH_VARARGS,
	 "initialize dht reader"},
	{"read", dhtreader_read, METH_VARARGS,
	 "temperature and humidity from sensor"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initdhtreader(void)
{
    PyObject *m;

    m = Py_InitModule("dhtreader", DHTReaderMethods);
    if (m == NULL)
        return;
}


