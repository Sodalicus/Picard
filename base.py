#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Sodalicus 
#
# Distributed under terms of the MIT license.

"""

"""

import sqlite3, os, datetime


db_file = 'data.db'

#DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
def del_db():
    if os.path.isfile(db_file):
        print(os.remove(db_file))
        print("Removed database file:"+db_file)

def create_db():
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

        con.commit()
        con.close()
        print("Created new empty database")

def retrive_data2():
    """Get data from the base"""
    con = sqlite3.connect(db_file)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    period = "datetime('now', '-24 hours')"
    sqlStatement = "SELECT * FROM reading WHERE time_added > (datetime('now', '-17 hours')) ;"
    cur.execute(sqlStatement)
    results = cur.fetchall()
    status = {'temp_ins0': [], 'temp_out0': [], 'datetime': []}
    for result in results:
        status['temp_ins0'].append(result['temp_ins0'])
        status['temp_out0'].append(result['temp_out0'])
        status['datetime'].append(result['time_added'])
    return status


print(retrive_data2())

#del_db()
#create_db()



def fake_temp(a,b):
    """Return fake arduino output"""
    import random
    temp = (random.randrange(1000, 3000)/100)
    states = "1:1:1:1:"+str(temp)
    return states

# ID; DEV01; DEV02; DEV03; DEV04; TEMP_INS0; TEMP_INS1; TEMP_OUT0; DATETIME;


