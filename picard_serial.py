#! /usr/bin/env python2
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Paweł Krzemiński 
#
# Distributed under terms of the MIT license.


"""
"""

import time, serial, os
import selectors
from picard_base import add_reading

# Serial port setup



def find_usb_dev():
    """Return current path to arduino's clone serial device"""
    for x in range(10):
        usbDev = r"/dev/ttyUSB"+str(x)
        if os.path.exists(usbDev):
            return usbDev
        else:
            return None

def setup_serial():
    """setup serial object and return it"""
    usbPort = find_usb_dev()
    if not usbPort: return None
    if os.path.exists(usbPort):
        ser = serial.Serial(
           port=usbPort,
           baudrate = 9600,
           parity=serial.PARITY_NONE,
           stopbits=serial.STOPBITS_ONE,
           bytesize=serial.EIGHTBITS,
           timeout=1)
        return ser
    else:
        return None

def talk_to_ard(cmdIndex):
    """Send byte literal through usb port to arduino, read and return a list"""
    ser = setup_serial()
    cmdCode = [b'1\n',b'2\n',b'3\n',b'4\n',b'5\n',b'6\n',b'7\n',b'x\n']
    if cmdIndex >= len(cmdCode): return None
    if ser:
        ser.write(cmdCode[cmdIndex])
        byteString = ser.readline()
        ser.close()

        text = byteString.decode().rstrip()
        response = text.split(":")
        return response
    else:
        return None

def talk_to_ard2(cmd):
    ser = setup_serial()
    ser.write(cmd)
    ser.close()


def full_message(msg):
    print(msg)
    print()


class SerialConnection:
    """Object that handles incoming data from serial port"""
    def __init__(self):
        """Initialize state variables. """
        self.receiving = False
        self.msg = ""

    def read_serial(self, key):
        """Read byte from serial port and pass it further."""
        ser = key.fileobj
        self.construct_msg(ser.read().decode())

    def construct_msg(self, incChar):
        """Construct message from incoming characters, know begining\
           and ending delimiters ;[...];"""
        if incChar == ";" and self.receiving == 0:
            self.receiving = 1
        elif incChar == ";" and self.receiving > 0:
            full_message(self.msg)
            self.service_msg(self.msg)
            self.receiving = 0
            self.msg = ""
        else:
            self.msg += incChar

    def service_msg(self, msg):
        """Message consist of four numbers seperated by colons.\
           example: '0:1:32.40:34'
           Check if we've got full message and work with it"""

        pass
        msg = msg.split(":")
        if len(msg) == 4:
            add_reading(1, msg[2])



def main():
    ser = setup_serial()

    sel = selectors.DefaultSelector()
    sel.register(ser, selectors.EVENT_READ, data="ard")
    incChar = ""
    receiving = 0
    msg = ""
    while True:
        events = sel.select(timeout=0)
        if events:
            for key, mask in events:
                incChar = ser.read().decode()
                if incChar == ";" and receiving == 0:
                    receiving = 1
                elif incChar == ";" and receiving > 0:
                    full_message(msg)
                    receiving = 0
                    msg = ""
                else:
                    msg += incChar
def main2():
    print(talk_to_ard(7))


if __name__ == "__main__":
    main2()
