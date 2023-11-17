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
from picard_base import get_recent_temp, select_radio
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
    data.inBuf += recvData
    if len(data.inBuf) >= 8:
        print("data.inBuf >= 8")
        print("data.inBuf=", data.inBuf)
        command = data.inBuf.decode('ascii')
        control(command)
        selector.unregister(conn)
        conn.close()

    """value is a code received from remote control"""
def remote_control(value):

    actions = {12 : "channel 1",\
               24 : "channel 2",\
               94 : "channel 3",\
               8  : "channel 4",\
               28 : "channel 5",\
               90 : "channel 6",\
               66 : "channel 7",\
               82 : "channel 8",\
               74 : "channel 9",\
               9  : "radio stop",\
               7  : "volume -",\
               21 : "volume +",\
               25 : "lamp motion",\
               13 : "lamp turn", \
               70 : "temperature",\
               74 : "exit"}
    if value in actions.keys():
        control(actions[value])

def control(command):
    print("command: {}".format(command))
    """ accepts string space seperated 'action value'"""
    command = command.split()
    print("command: {}".format(command))

    if len(command) == 2:
        """ double word commands """

        if command[0] == "volume":
            """ Volume manipulation """
            if command[1] == "+":
                print("volume up")
                radio.volume_up()
                display.msg(str(radio.return_volume()))
            elif command[1] == "-":
                print("volume down")
                radio.volume_down()
                display.msg(str(radio.return_volume()))
            else:
                try:
                    volume = int(command[1])
                    radio.volume_set(volume)

                except ValueError:
                    print("Incorrect volume, not an integer.")

        if command[0] == "channel":
            """ Channel manipulation """
            if command[1] == "default":
                pass
            elif command[1] == "+":
            # channel up
                pass
            elif command[1] == "-":
            # channel down
                pass
            else:
                try:
                    number = int(command[1])
                    radio_channel = select_radio(number)
                    if radio_channel != None:
                        radio.play(radio_channel['url'], radio_channel['name'])

                    print("Selected channel number {0}, name {1}, source {2}".format(command[1],\
                            radio_channel['name'], radio_channel['url']))
                except ValueError:
                    print("Incorrect channel number, not an integer.")



        if command[0] == "lamp":
            """ lamp control """
            if command[1] == "motion":
                talk_to_ard2(b'x\n')
            elif command[1] == "turn":
                talk_to_ard2(b'y\n')

        if command[0] == "radio":
            """ Radio object manipulation """
            if command[1] == "stop":
                radio.stop()

    elif len(command) == 1:
        """ single word commands """
        if command[0] == "temperature":
           display.msg(get_recent_temp()[0])
        elif command[0] == "exit":
            sys.exit()
    else:
        print("Unknown command {}".format(command))



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
