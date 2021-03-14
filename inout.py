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

usbPort = '/dev/ttyUSB0'
# Serial port setup

dataToSend = b'3\n'

def talk_to_ard(usbPort, dataToSend):
    if os.path.exists(usbPort):
        ser = serial.Serial(
           port=usbPort,
           baudrate = 9600,
           parity=serial.PARITY_NONE,
           stopbits=serial.STOPBITS_ONE,
           bytesize=serial.EIGHTBITS,
           timeout=1)
    else:
        return(1)

    ser.write(dataToSend)
    x = ser.readline()
    text = x.decode()
    ser.close()
    return(text)

#print(talk_to_ard(usbPort, dataToSend))

"""
time0 = time.time()
text2 = ["0","0"]
while True:
    x = ser.readline()
    text = x.decode('ascii')
    if time.time() - time0 > 0.1:
        time0 = time.time()
        if text:
            text2 = text.split(",")
"""
