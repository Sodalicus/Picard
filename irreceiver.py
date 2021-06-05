#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 pi <pi@pipboy5000>
#
# Distributed under terms of the MIT license.

"""
InfraRed remote control for picard.
It one way communicates with flask app by sending HTTP Post requests,
and so it's completly separate.

Key down event values for my remote:
    69,70,71
    68,64,67
     7,21, 9
    22,25,13
    12,24,94
     8,28,90
    66,82,74

    69,70,71,68,64,67,7,21,9,22,25,13,12,24,94,8,28,90,66,82,74

"""
import evdev
import requests
import time

appUrl = "http://127.0.0.1:5000/"
device = evdev.InputDevice('/dev/input/event0')
actions = {70 : "radio", 71 : "noise", 7 : "volumedown", 21 : "volumeup", 12 : "switch", 24: "switch"}

device_switches= [{ "dev_switch" : "1"},{ "dev_switch" : "2"}]

t0 = time.time()
diff = 1

print(device)

for event in device.read_loop():
    if (event.value) in actions.keys():
        t1 = time.time()
        if (t1 - t0) > diff:
            t0 = time.time()
            if event.value == 12:
                requests.post(appUrl+actions[event.value], data = device_switches[1])
            elif event.value == 24:
                requests.post(appUrl+actions[event.value], data = device_switches[2])
            else:
                requests.post(appUrl+actions[event.value])
    else:
        print(event.value)
