#!/usr/bin/env python
# coding=latin1

"""
This plugin requires the Dataloop agent user to be in the spi and i2c groups or to be run as root.

The Adafruit TSL2561 directory available as part of the Raspberry Pi Python library from

https://github.com/IainColledge/Adafruit-Raspberry-Pi-Python-Code

Will update to use the Adafruit library when they accept one of two TSL2561 module pull requests.

The directory should be copied to the dataloop plugins directory /opt/dataloop/plugins and a blank file __init__.py
added then this file should be copied to /opt/dataloop/plugins so the file structure looks like

tsl2561.lux.py
Adafruit_TSL2561/Adafruit_I2C.py
Adafruit_TSL2561/Adafruit_TSL2561.py
Adafruit_TSL2561/__init__.py

Changelog:
1.0 Initial release - Iain Colledge

Iain Colledge
"""

import Adafruit_TSL2561.Adafruit_TSL2561 as Adafruit_TSL2561

LightSensor = Adafruit_TSL2561.AdafruitTSL2561()
LightSensor.enable_auto_gain(True)

try:
    lux = int(LightSensor.calculate_avg_lux())
except OverflowError as e:
    # Peg at max value possible
    lux = 65535

print "OK| lux=%d;;;;" % lux
