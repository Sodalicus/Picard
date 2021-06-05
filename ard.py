#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Sodalicus 
#
# Distributed under terms of the MIT license.


"""
"""

import time, serial, os

# Serial port setup



def find_usb():
    """Return current path to arduino's clone serial device"""
    for x in range(10):
        usbDev = r"/dev/ttyUSB"+str(x)
        if os.path.exists(usbDev):
            return usbDev
        else:
            return None

def talk_to_ard(cmdIndex):
    """Send byte literal through usb port to arduino, read and return a list"""
    usbPort = find_usb()
    cmdCode = [b'1\n',b'2\n',b'3\n',b'4\n',b'5\n',b'6\b']
    if cmdIndex >= len(cmdCode): return None

    if usbPort == None: return None

    if os.path.exists(usbPort):
        ser = serial.Serial(
           port=usbPort,
           baudrate = 9600,
           parity=serial.PARITY_NONE,
           stopbits=serial.STOPBITS_ONE,
           bytesize=serial.EIGHTBITS,
           timeout=1)
    else:
        return None

    ser.write(cmdCode[cmdIndex])
    byteString = ser.readline()
    ser.close()

    text = byteString.decode().rstrip()
    response = text.split(":")
    return response


