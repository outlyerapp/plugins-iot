#!/usr/bin/env python
# coding=latin1

'''
This plugin requires the Dataloop agent user to be in the spi and i2c groups or to be run as root.

The Adafruit BMP085 directory available as part of the Raspberry Pi Python library from

https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

It's depreciated for a version that works across the Pi and Beaglebone black but is easier to set up
with Dataloop so hence interfaced to here.

create a directory, Adafruit_BMP085, in /opt/dataloop/plugins
From the Adafruit_BMP085 directory, copy Adafruit_BMP085.py to /opt/dataloop/plugins/Adafruit_BMP085
From the Adafruit_I2C directory, copy Adafruit_I2C.py to /opt/dataloop/plugins/Adafruit_BMP085
Add a blank file __init__.py to /opt/dataloop/plugins/Adafruit_BMP085

The file structure should look in /opt/dataloop/plugins like

tsl2561.lux.py
Adafruit_BMP085/Adafruit_I2C.py
Adafruit_BMP085/Adafruit_BMP085.py
Adafruit_BMP085/__init__.py

Program comments from Adafruit_BMP_example.py

Iain Colledge
'''

import Adafruit_BMP085.Adafruit_BMP085 as Adafruit_BMP085

# Initialise the BMP085 and use STANDARD mode (default value)
# bmp = Adafruit_BMP085(0x77, debug=True)
bmp = Adafruit_BMP085(0x77)

# To specify a different operating mode, uncomment one of the following:
# bmp = BMP085(0x77, 0)  # ULTRALOWPOWER Mode
# bmp = BMP085(0x77, 1)  # STANDARD Mode
# bmp = BMP085(0x77, 2)  # HIRES Mode
# bmp = BMP085(0x77, 3)  # ULTRAHIRES Mode

temp = bmp.readTemperature()

# Read the current barometric pressure level
pressure = bmp.readPressure()

# To calculate altitude based on an estimated mean sea level pressure
# (1013.25 hPa) call the function as follows, but this won't be very accurate
#
# TODO: See if geolocating the IP can be done to find the nearest METAR and machine read local sea level pressure
altitude = bmp.readAltitude()

# To specify a more accurate altitude, enter the correct mean sea level
# pressure level.  For example, if the current pressure level is 1023.50 hPa
# enter 102350 since we include two decimal places in the integer value
# altitude = bmp.readAltitude(102350)

print "OK| temperature=%.2f°C;;;; pressure=%.2f°hPa;;;; altitude=%.2fm" % (temp, pressure / 100, altitude)