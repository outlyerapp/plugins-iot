#!/usr/bin/env python
# coding=latin1

"""
This plugin requires the Dataloop agent to be run as root
Update: /lib/systemd/system/dataloop-agent.service and set User=root
Run: systemctl restart dataloop-agent
"""

import RPi.GPIO as GPIO
import time

CHANNEL = 4  # BMC pin number

bits = [1] * 41


def read_bit():
    while GPIO.input(CHANNEL) == 0: pass
    start = time.time()
    delta = 0.0
    while GPIO.input(CHANNEL) == 1:
        delta = time.time() - start
        if delta > 0.000200:
            raise Exception("Timeout on reciving bit of data")
    return (delta >= 0.000040) and 1 or 0


def bits_to_int(bits):
    binary_string = "".join([str(x) for x in bits])
    return int(binary_string, 2)


# Wake up DHT11 and initialize transmission
GPIO.setmode(GPIO.BCM)
GPIO.setup(CHANNEL, GPIO.OUT)

GPIO.output(CHANNEL, GPIO.HIGH)
time.sleep(0.025)
GPIO.output(CHANNEL, GPIO.LOW)
time.sleep(0.02)

# Read 41 bits, with one extra
GPIO.setup(CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
for i in range(0, len(bits)):
    bits[i] = read_bit()

# First bit should be always, just a sigh DHT has started
if bits[0] != 1:
    raise Exception("Invalid transmission beginning")
bits = bits[1:]

decoded = [bits_to_int(bits[(i * 8):((i + 1) * 8)]) for i in range(0, len(bits) / 8)]

cksum = 0
for i in range(0, 4):
    cksum += decoded[i]
if decoded[4] != cksum % 256:
    raise Exception("Invalid check sum")

print "OK| humidity=%d%%;;;; temperature=%d°C;;;;" % (decoded[0], decoded[2])
