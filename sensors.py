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

db_file = "data1.db"
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


def save_status():
    """Save sensors reading and devices status to database"""
    if os.path.isfile(db_file):
        con = sqlite3.connect(db_file)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        status = get_status()
        if status != 1:
            cur.execute('INSERT INTO reading (dev01, dev02, dev03, dev04, temp_ins0, temp_ins1, hum_ins1, temp_out0, alive) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', status)
            con.commit()
            con.close()
    else:
        print("Database file doesn's exist")
#save_status()

def fake_temp():
    """Return fake arduino output"""
    temp = (random.randrange(1000, 3000)/100)
    return temp
#print(fake_temp())

def fake_status():
    """Fill the database with generated data, so with we have something to work with"""
    status = []
    for i in range(4):
        status.append(str(random.randint(0,1)))
    for i in range(4):
        status.append(str(fake_temp()))
    status.append(str(random.randint(0,1)))
    return status

def save_fake_status(db_file):
    """Save sensors reading and devices status to database"""
    timeNow = time.time()
    timeReduced = timeNow
    threeDays = timeReduced-(259200)

    #date_now = time.strftime("%Y-%m-%d %H:%M:%S")
    while timeReduced > threeDays:
        timeReduced -= 300
        timeTupleNow = time.localtime(timeReduced)
        dateNow = time.strftime("%Y-%m-%d %H:%M:%S", timeTupleNow)
        if os.path.isfile(db_file):
            con = sqlite3.connect(db_file)
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            status = fake_status()
            status.append(dateNow)
            if status != 1:
                cur.execute('INSERT INTO reading (dev01, dev02, dev03, dev04, temp_ins0, temp_ins1, hum_ins1, temp_out0, alive, time_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', status)
                con.commit()
                con.close()
        else:
            return 1
    return 0


def main():
    while True:
        save_status()
        talk_to_ard(usbPort, b'5\n')
        print("*")
        time.sleep(180)

#main()
