#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Paweł Krzemiński
#
# Distributed under terms of the MIT license.

"""
Main

Key down event values for my remote:
    69,70,71
    68,64,67
     7,21, 9
    22,25,13
    12,24,94
     8,28,90
    66,82,74

    69,70,71,68,64,67,7,21,9,22,25,13,12,24,94,8,28,90,66,82,74
    to record 1 channel audio, 640x480 video from webcam
ffmpeg -ac 1 -f alsa -i hw:1 -f v4l2 -video_size 640x480 -i /dev/video0 public/test.flv
"""

import selectors # for reading irDa and sockets
import socket
from picard_radio import Radio
from picard_base import get_radios, get_def_radio, get_recent_temp
from picard_serial import setup_serial, SerialConnection, talk_to_ard2
from picard_lib import load_config
import time
import sys
import types

SETTINGS = load_config()
ADDR = (SETTINGS["SADDRESS"],SETTINGS["SPORT"])
IRDA_DEV = SETTINGS["IRDA_DEV"]

selector = selectors.DefaultSelector()

if SETTINGS["USE_DISPLAY"] == "True":
    from picard_7sd import SevenSegDisplay
    display = SevenSegDisplay()
else:
    from picard_lib import DummyDisplay
    display = DummyDisplay()

if SETTINGS["USE_IRDA"] == "True":
    from evdev import InputDevice # for reading IrDa
    #Setup InfraRed input - for remote control
    irda = InputDevice(IRDA_DEV)
    if irda:
        selector.register(irda, selectors.EVENT_READ, data="remote")




radio = Radio()
radios = get_radios()


#Setup socket input - for client program
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind(ADDR)
lsock.listen()
lsock.setblocking(False)
selector.register(lsock, selectors.EVENT_READ, data="accept")

#Setup serial input - for communication with arduino
ser = setup_serial()
if ser:
    selector.register(ser, selectors.EVENT_READ, data="read_serial")
    serConn = SerialConnection()

def accept_connection(key):
    socket = key.fileobj
    conn, ADDR = socket.accept()
    conn.setblocking(False)
    data = types.SimpleNamespace(inBuf=b'')
    selector.register(conn, selectors.EVENT_READ, data=data)


def service_connection(key):
    conn = key.fileobj
    data = key.data
    recvData = conn.recv(1024)
    print("recvData", recvData)
    data.inBuf += recvData
    if len(data.inBuf) >= 8:
        print("data.inBuf >= 8")
        print("data.inBuf=", data.inBuf)
        value = data.inBuf.decode('ascii')
        front_control(value)
        selector.unregister(conn)
        conn.close()


def front_control(value):
    """Value is a data from the client received by the socket"""
    actions = ["radio_01",\
               "radio_02",\
               "radio_03",\
               "radio_04",\
               "radio_05",\
               "radio_06",\
               "radio_07",\
               "radio_08",\
               "radio_09",\
               "radio_def",\
               "radio_stop",\
               "volume_up",\
               "volume_down",\
               "motion_light",\
               "night_light",\
               "exit"]
    if value in actions:
        control(value)


def remote_control(value):
    """value is a code received from remote control"""

    actions = {12 : "radio_01",\
               24 : "radio_02",\
               94 : "radio_03",\
               8  : "radio_04",\
               28 : "radio_05",\
               90 : "radio_06",\
               66 : "radio_07",\
               82 : "radio_08",\
               74 : "radio_09",\
               67 : "radio_def",\
               9  : "radio_stop",\
               7  : "volume_down",\
               21 : "volume_up",\
               70 : "temperature",\
               74 : "exit"}
    if value in actions.keys():
        control(actions[value])
        #sys.exit()

def control(value):
    if value == "volume_up":
        print("volume up")
        radio.volume_up()
        display.msg(str(radio.return_volume()))
    elif value == "volume_down":
        print("volume down")
        radio.volume_down()
        display.msg(str(radio.return_volume()))
    elif value == "radio_def":
        radioDef = get_def_radio()
        if radioDef != None:
            radio.play(radioDef['url'],radioDef['name'])
    elif value == "radio_stop":
        radio.stop()
    elif value in get_radios():
        radio.play(radios[value]['url'],radios[value]['name'])
        display.msg(radios[value]['name'])
    elif value == "temperature":
        display.msg(get_recent_temp()[0])
    elif value == "motion_light":
        talk_to_ard2(b'x\n')
    elif value == "night_lamp":
        talk_to_ard2(b'y\n')
    elif value == "exit":
        sys.exit()
    else:
        pass


print("Starting picard...")
t0 = time.time()
t00 = time.time()
while True:
    #print(time.time())
    t1 = time.time()
    if (t1 - t0) > 20:
        display.update_clock()
        t0 = time.time()
    for key, mask in selector.select(timeout=0):
        # We received something on irda
        if key.data == "remote":
                device = key.fileobj
                for event in device.read():
                    if (t1 - t00) > 0.1:
                        print(event.value)
                        remote_control(event.value)
                        t00 = time.time()
        # We've got incoming socket socket connection
        elif key.data == "accept":
            accept_connection(key)
        elif key.data == "read_serial":
            serConn.read_serial(key)
        else:
        # We've got active connection to read
            service_connection(key)
