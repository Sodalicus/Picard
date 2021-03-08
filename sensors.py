#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Sodalicus 
#
# Distributed under terms of the MIT license.

"""

"""
import sqlite3, os, time
import random
from inout import talk_to_ard

db_file = "data.db"
DELAY = 180
t0 = time.time()
usbPort = '/dev/ttyUSB0'
dataToSend = b'4\n'

def temp_time():
    """Return temperature reading and current timestamp"""
    temp = talk_to_ard(usbPort, dataToSend)
    temp = float(temp)
    return temp, time.strftime("%Y-%m-%d %H:%M:%S")


def save_temp():
    if os.path.isfile(db_file):
        con = sqlite3.connect(db_file)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        temp = temp_time()
        print(temp)

        cur.execute('INSERT INTO sensors VALUES (NULL, ?, ?);',
                temp)
        con.commit()
        con.close()

while True:
    time.sleep(3)
    save_temp()
    print("*")
