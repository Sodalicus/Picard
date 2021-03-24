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
#current_time = time.strftime("%Y-%m-%d,%H:%M:%S")
dataToSend = b'6\n' # this code just makes arduino just return status

def get_status():
    """Return temperature reading and current timestamp"""
    status = talk_to_ard(usbPort, dataToSend)
    if status != 1:
        status = status.split(":")
        return status
    else:
        return(1)

#print(get_status())

def save_status():
    if os.path.isfile(db_file):
        con = sqlite3.connect(db_file)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        status = get_status()
        if status != 1:
            cur.execute('INSERT INTO reading (dev01, dev02, dev03, dev04, temp_ins0, temp_ins1, hum_ins1, temp_out0, alive) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', status)
            con.commit()
            con.close()
#save_status()

def main():
    while True:
        save_status()
        talk_to_ard(usbPort, b'5\n')
        print("*")
        time.sleep(180)

main()
