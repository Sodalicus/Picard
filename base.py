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

def create_db():
    """Create new db if it doesn`t exist"""
    if not os.path.isfile(db_file):
        con = sqlite3.connect(db_file)
        cur = con.cursor()
        cur.executescript("""
                CREATE TABLE IF NOT EXISTS sensor (
                id INTEGER PRIMARY KEY ASC,
                name VARCHAR NOT NULL,
                description VARCHAR);""")
        cur.executescript("""
                CREATE TABLE IF NOT EXISTS reading (
                id INTEGER PRIMARY KEY ASC,
                temp FLOAT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                source INTEGER NOT NULL,
                FOREIGN KEY(source) REFERENCES sensor(id));""")
        cur.execute("INSERT INTO sensor VALUES(NULL, ?, ?);", ('DS18B20', "temperature sensor"))


        con.commit()
        con.close()

create_db()


