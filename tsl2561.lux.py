#!/usr/bin/env python
# coding=latin1

'''
This plugin requires the Dataloop agent to be in the spi and i2c groups or to be run as root.

The Adafruit TSL2561 directory available as part of the Pi 2 Python library from

https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

Should be copied to the dataloop plugins directory /opt/dataloop/plugins and a blank file __init__.py added

Iain Colledge
'''

import Adafruit_TSL2561.Adafruit_TSL2561 as Adafruit_TSL2561

LightSensor = Adafruit_TSL2561.Adafruit_TSL2651()
LightSensor.enableAutoGain(True)

print "OK| lux=%d;;;;" % (int(LightSensor.calculateAvgLux()))