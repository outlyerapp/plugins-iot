#!/usr/bin/env python
# coding=latin1

"""
This plugin requires the Dataloop agent user to be in the spi and i2c groups or to be run as root.

The Adafruit BMP085 directory available as part of the Raspberry Pi Python library from

https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

It's depreciated for a version that works across the Pi and Beaglebone black but is easier to set up
with Dataloop so hence interfaced to here.

Create a directory, Adafruit_BMP085, in /opt/dataloop/plugins
From the Adafruit_BMP085 directory, copy Adafruit_BMP085.py to /opt/dataloop/plugins/Adafruit_BMP085
From the Adafruit_I2C directory, copy Adafruit_I2C.py to /opt/dataloop/plugins/Adafruit_BMP085
Add a blank file __init__.py to /opt/dataloop/plugins/Adafruit_BMP085

The file structure should look in /opt/dataloop/plugins like

bmp085.temp_press_alt.py
Adafruit_BMP085/Adafruit_I2C.py
Adafruit_BMP085/Adafruit_BMP085.py
Adafruit_BMP085/__init__.py

Some script comments below from Adafruit_BMP_example.py

Changelog:
1.12 Added sea level presure to outputs, changed references to surface pressure to sea level pressure. - Iain Colledge
1.11 Use last know good sea level pressure instead of default of 1013 in case of METAR failure. - Iain Colledge
1.1 Added geolocation with Metars for setting sea level pressure and syslogging - Iain Colledge
1.0 Initial release interfacing to Adafruit BMP085 drivers - Iain Colledge

"""

import logging
import Adafruit_BMP085.Adafruit_BMP085 as Adafruit_BMP085
import json
import requests
import os
import syslog
from datetime import timedelta

# Persistent cache
TMPDIR = '/opt/dataloop/tmp'
TMPFILE = 'bmp085.json'

# IP Address Geolocation API
geoloc_api = "https://freegeoip.net/json/"
# METAR API
metar_api = "http://avwx.rest/api/metar.php"
# STD sea level pressure in hPa
sea_level_pressure = 1013

syslog.openlog(logoption=syslog.LOG_DAEMON)


def uptime():
    """
    Reads system uptime and converts into a handy tuple for use in a script

    :return: tuple of uptime broken down into the days, hours, minutes, seconds, microseconds since start
    """
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        sys_uptime = timedelta(seconds=uptime_seconds)
        f.close()

    days_up = sys_uptime.days
    hours_up = sys_uptime.seconds / 3600
    minutes_up = (sys_uptime.seconds % 3600) / 60
    seconds_up = (sys_uptime.seconds % 3600) % 60
    microseconds_up = sys_uptime.microseconds

    return days_up, hours_up, minutes_up, seconds_up, microseconds_up


def tmp_file():
    """
    Creates a temporay persistence file

    :return: True if already existed, False if not
    """
    if not os.path.isdir(TMPDIR):
        os.makedirs(TMPDIR)
    if not os.path.isfile(TMPDIR + '/' + TMPFILE):
        os.mknod(TMPDIR + '/' + TMPFILE)
        return False
    else:
        return True


def get_cache():
    """
    Returns the cached sea level pressure or the default if unable to do so

    :return:
    """
    with open(TMPDIR + '/' + TMPFILE, 'r') as json_fp:
        try:
            json_data = json.load(json_fp)
            json_fp.close()
        except Exception, excep:
            syslog.syslog(syslog.LOG_ERR, "cache file " + TMPDIR + "/" + TMPFILE + " is unreadable: " + str(excep))
            return sea_level_pressure
    return json_data


def write_cache(cache):
    """
    Writes the parameter as a JSON formatted cache value

    :param cache: object to be cached
    """
    with open(TMPDIR + '/' + TMPFILE, 'w') as json_fp:
        try:
            json.dump(cache, json_fp)
            json_fp.close()
        except Exception, excep:
            syslog.syslog(syslog.LOG_ERR, "unable to write to cache file " + TMPDIR + "/" + TMPFILE + ": " + str(excep))


def delete_cache():
    """
    Deletes the tempory cache file

    """
    try:
        os.remove(TMPDIR + '/' + TMPFILE)
    except Exception, excep:
        syslog.syslog(syslog.LOG_ERR, "failed to delete cache file " + TMPDIR + "/" + TMPFILE + ": " + str(excep))


# Limit the geolocation update to once per hour calculated since bootup as both the geoloc and metar API's are free
# and can block if used too much and anyway don't want to abuse the service if no need to.
#
# Once per hour using uptime is used so as to randomize any requets coming into these APIs from different Pi's
# around the world.

days, hours, minutes, seconds, microseconds = uptime()

# Update the sea level pressure once per hour since uptime or when the tmp file is created
# Should be enough for vehicles like cars or trains, else update every call if in a drone / aircraft

existing_tmp_file = tmp_file()

if (minutes == 59 and seconds < 30) or (not existing_tmp_file):
    # Geolocate the IP
    try:
        response = requests.get(geoloc_api)
        if response.status_code == 200:
            jsondata = json.loads(response.content)
            latitude = jsondata["latitude"]
            longitude = jsondata["longitude"]
            try:
                # Get the nearest METAR
                response = requests.get(metar_api, params={'lat': latitude, 'lon': longitude, 'format': 'JSON'})
                if response.status_code == 200:
                    jsondata = json.loads(response.content)
                    altimeter = int(jsondata["Altimeter"])
                    altimeter_units = jsondata["Units"]["Altimeter"]
                    station = jsondata["Station"]
                    metar_time = jsondata["Time"]
                    # Convert fom inMg to hPa if inside US
                    if altimeter_units == "hPa":
                        sea_level_pressure = altimeter
                    else:
                        sea_level_pressure = altimeter * 33.86389
                    message = ("at uptime " + str(days) + ":" + str(hours) + ":" + str(minutes) + ":" + str(seconds) +
                               " sea level pressure " + str(sea_level_pressure) +
                               "hPa set for lat:" + str(latitude) + ", lon:" + str(longitude) +
                               " using METAR from " + station + " at " + metar_time + " time")
                    syslog.syslog(syslog.LOG_INFO, message)
                    print(message)
            except Exception, e:
                syslog.syslog(syslog.LOG_WARNING,
                              "unable to get METAR for lat: " + str(latitude) + ", lon:" + str(longitude) + " : " + str(
                                      e))
                # Use the last known good for sea level pressure for the next time period
                sea_level_pressure = get_cache()
        write_cache(sea_level_pressure)
    except Exception, e:
        syslog.syslog(syslog.LOG_WARNING, "unable to get lat, long coords : " + str(e))
else:
    sea_level_pressure = get_cache()

# Initialise the BMP085
#
# To specify different operating mode, uncomment one of the following:
# bmp = Adafruit_BMP085.BMP085(0x77) # and use STANDARD mode (default value)
# bmp = Adafruit_BMP085.BMP085(0x77, debug=True) # and use STANDARD mode (default value) with debugging info
# bmp = Adafruit_BMP085.BMP085(0x77, 0)  # ULTRALOWPOWER Mode
# bmp = Adafruit_BMP085.BMP085(0x77, 1)  # STANDARD Mode
# bmp = Adafruit_BMP085.BMP085(0x77, 2)  # HIRES Mode
bmp = Adafruit_BMP085.BMP085(0x77, 3)  # ULTRAHIRES Mode

temp = bmp.readTemperature()

# Read the current barometric pressure level
pressure = bmp.readPressure()

# To calculate altitude based on an estimated mean sea level pressure
# (1013.25 hPa) call the function as follows, but this won't be very accurate
#
# The STD pressure of 1013.25 hPa is an approximation but depending on high or low weather pressure will
# generally be innacurate unless a known sea level pressure for that location is used.
#
# You'll also see some noise between readings as barometric altemeters are noisy by nature, especially for such
# a low cost device and also because METARs are whole numbers why planes use radar altimeters
# for the last couple of thousand feet

altitude = bmp.readAltitude(int(sea_level_pressure * 100))

# To specify a more accurate altitude, enter the correct mean sea level
# pressure level.  For example, if the current pressure level is 1023.50 hPa
# enter 102350 since we include two decimal places in the integer value
# altitude = bmp.readAltitude(102350)

syslog.closelog()

print "OK| temperature=%.2f°C;;;; pressure=%.2fhPa;;;; sea_level_pressure=%dhPa;;;; altitude=%.2fm;;;;" % (
    temp, pressure / 100, sea_level_pressure, altitude)
