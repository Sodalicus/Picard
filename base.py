#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Sodalicus 
#
# Distributed under terms of the MIT license.

"""

"""

import sqlite3, os, datetime, time, csv
import random
from ard import talk_to_ard

db_file = 'data.db'

def load_from_csv(csvFile):
    """Load data from csv file and return table"""
    if os.path.isfile(csvFile):
        with open(csvFile) as file:
            lines = file.readlines()
            data_from_csv = []
            for row in csv.reader(lines, delimiter=";"):
                data_from_csv.append(row)
        return data_from_csv
    else:
        return 1

def del_db(db_file):
    """Delete db file"""
    if os.path.isfile(db_file):
        os.remove(db_file)
        return 0
    else:
        return 1

def create_db(db_file):
    """Create new db if it doesn`t exist"""
    if not os.path.isfile(db_file):
        con = sqlite3.connect(db_file)
        cur = con.cursor()
        cur.executescript("""
                CREATE TABLE IF NOT EXISTS reading (
                id INTEGER PRIMARY KEY ASC,
                dev01 BOOL,
                dev02 BOOL,
                dev03 BOOL,
                dev04 BOOL,
                temp_ins0 FLOAT NOT NULL,
                temp_ins1 FLOAT NOT NULL,
                hum_ins1 INTEGER NOT NULL,
                temp_out0 FLOAT NOT NULL,
                alive INTEGER NOT NULL,
                time_added INT DEFAULT (datetime('now', 'localtime')));""")

        cur.executescript("""
                CREATE TABLE IF NOT EXISTS device (
                id INTEGER PRIMARY KEY ASC,
                name TEXT NOT NULL,
                unit TEXT,
                switchable BOOL NOT NULL,
                outside BOOL NOT NULL,
                description TEXT
                );""")
        con.commit()
        con.close()
        return 0
    else:
        return 1

def fill_default(db_file):
    """Fill device table with defaults"""
    if os.path.isfile(db_file):
        con =sqlite3.connect(db_file)
        cur = con.cursor()
        cur.execute("DELETE FROM device")
        dev_defs = load_from_csv("devices.csv")
        for dev in dev_defs:
            cur.execute('INSERT INTO device (name, unit, switchable, outside, description) VALUES(?, ?, ?, ?, ?)', dev)
        con.commit()
        con.close()


def get_status():
    """Return temperature reading and current timestamp"""
    status = talk_to_ard(dataToSend)
    if status != None:
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
    choice = ""
    while choice != "0":
        print("\n\nWhat do you want to do: ")
        print("1. Create new empty db.")
        print("2. Fill empty db with defaults")
        print("3. Fill empty db with 'fresh' random data.")
        print("4. Delete current db")
        print("0. Quit")
        choice = input("choice: ")
        if choice == "1":
            if create_db(db_file) == 0:
                print("created new empty db.")
            else:
                print("db already exists.")
        if choice == "2":
            fill_default(db_file)
        if choice == "3":
            if save_fake_status(db_file) == 0:
                print("random crap inserted")
            else:
                print("db file doesn't exist")
        if choice == "4":
            if del_db(db_file) == 0:
                print("db file deleted")
            else:
                print("db file doesn't exist")



if __name__ == "__main__":
    main()
