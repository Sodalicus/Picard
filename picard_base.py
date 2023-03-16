#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Paweł Krzemiński
#
# Distributed under terms of the MIT license.

"""

"""
import sqlite3
from picard_lib import load_config

SETTINGS = load_config()
DBFILE = SETTINGS["DBFILE_PATH"]+SETTINGS["DBFILE"]

DEF_RADIOS = [{ 'id': 1, 'name' : "chilldeep",\
        'url' :  "https://ch02.cdn.eurozet.pl/CHIDEP.mp3",\
        'defRadio' : False },
        { 'id' : 2, 'name' : "antyradio",\
        'url' :"http://an01.cdn.eurozet.pl/ant-waw.mp3",\
        'defRadio' : True },
        { 'id' : 3, 'name' : "eskarock",\
        'url' : "http://waw01-02.ic.smcdn.pl:8000/5380-1.aac.m3u",\
        'defRadio' : False },
        { 'id' : 4, 'name' : "radioOrbit",\
        'url' : "https://s1.slotex.pl/shoutcast/7390/stream#.mp3",\
        'defRadio' : False }]

DEF_SENSORS = [{ 'name' : "DS18B20", 'location' : "Inside",\
        'unit' : "Celsius" }]
DEF_SENSORS_LIST = ["DS18B20", "Inside", "Celsius"]


class DBase():
    def __init__(self, file=DBFILE):
        self.file = file
    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        self.conn.row_factory = sqlite3.Row
        return self.conn.cursor()
    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

def create_empty_db():
    with DBase() as cur:
        cur.execute("DROP TABLE IF EXISTS radios;")
        cur.execute("""CREATE TABLE IF NOT EXISTS radios (
                     id INTEGER PRIMARY KEY ASC,
                     name VARCHAR(256) DEFAULT NULL,
                     url VARCHAR(256) DEFAULT NULL,
                     defRadio BOOLEAN DEFAULT FALSE);""")
        for i in range(1,11):
            cur.execute("INSERT INTO radios default VALUES;")

        cur.execute("DROP TABLE IF EXISTS sensors;")
        cur.execute("""CREATE TABLE IF NOT EXISTS sensors (
                       id INTEGER PRIMARY KEY ASC,
                       name VARCHAR(256) NOT NULL,
                       location VARCHAR(256) NOT NULL,
                       unit VARCHAR(256) NOT NULL);""")

        '''
        cur.execute("DROP TABLE IF EXISTS readings;")
        cur.execute("""CREATE TABLE IF NOT EXISTS readings (
                       id INTEGER PRIMARY KEY ASC,
                       sensor_id INTEGER NOT NULL,
                       value FLOAT NOT NULL,
                       timestamp INT DEFAULT (datetime('now', 'localtime')),
                       FOREIGN KEY (sensor_id) REFERENCES sensors(id));""")
        '''

        cur.execute("DROP TABLE IF EXISTS player;")
        cur.execute("""CREATE TABLE IF NOT EXISTS player (
                       id INTEGER PRIMARY KEY ASC,
                       nowName VARCHAR(256),
                       nowUrl VARCHAR(256),
                       volume INT );""")
        cur.execute("INSERT INTO player VALUES(NULL, ?, ?, ?);", ("Nothing", "None", 0))

def update_volume(volume):
    """update player table with volume value"""
    with DBase() as cur:
        if volume:
            cur.execute("UPDATE player SET volume=? WHERE id=?;", (volume, "1"))

def get_volume():
    """return volume from player table"""
    with DBase() as cur:
        cur.execute("SELECT volume FROM player WHERE id=?;", ("1"))
        data = cur.fetchone()
        if data == None: return None
        volume = data['volume']
        print("x: {}".format(volume))
        return volume

def update_now_playing(nowPlaying):
    """nowPlaying = (name,url), update player table row(id=1) """
    name = nowPlaying[0]
    url = nowPlaying[1]
    with DBase() as cur:
        cur.execute("UPDATE player SET nowName=?,nowUrl=? WHERE id=?;", (name, url, "1"))

def get_now_playing():
    """Retrive and return name,url of radio currently being player\
       from the table"""
    with DBase() as cur:
        cur.execute("SELECT nowName,nowUrl FROM player WHERE id=?;", ("1"))
        data = cur.fetchone()
        if data == None: return None
        return (data['nowName'], data['nowUrl'])


def add_sensor(sensor):
    """add a new sensor(name, location, unit) to the sensors table"""
    if sensor and len(sensor) == 3:
        name = sensor[0]
        location = sensor[1]
        unit = sensor[2]
        with DBase() as cur:
            cur.execute("INSERT INTO sensors VALUES(NULL, ?, ?, ?);",(name, location, unit))

def add_reading(sensor_id, value):
    """ sensor_id is an id of a sensor from sensors table,
        value is a sensor's reading to save. """
    with DBase() as cur:
        cur.execute("INSERT INTO readings(sensor_id, value) VALUES(?, ?);",(sensor_id, value))

def get_recent_temp():
    """return most recent temperature reading and timestamp"""
    with DBase() as cur:
        cur.execute("""SELECT value,timestamp FROM readings WHERE sensor_id=1 ORDER BY \
                        timestamp DESC LIMIT 1;""")
        tempDate = cur.fetchone()
        if tempDate == None: return None
        temp = tempDate['value']
        timestamp = tempDate['timestamp']
        return temp,timestamp



def get_radios():
    with DBase() as cur:
        cur.execute("SELECT * FROM radios LIMIT 10")
        radios = cur.fetchall()
        radiosDict = {}
        radioNumber = 1
        if len(radios) == 0: return None
        for radio in radios:
            radioDict = { 'id': radio['id'], 'name' : radio['name']\
                    , 'url' : radio['url'], 'defRadio' : radio['defRadio'] }
            radiosDict['radio_0'+str(radioNumber) if radioNumber < 10 else 'radio_10'] = radioDict
            radioNumber += 1
        return radiosDict


def get_def_radio():
    """Return dictionary of name and url of default radio from the radios table,\
       or None if it doesn't exist."""
    with DBase() as cur:
        cur.execute("SELECT * FROM radios WHERE defRadio=True;")
        defRadio = cur.fetchone()
        if defRadio!=None:
            return {'name' : defRadio['name'], 'url' : defRadio['url']}
        else: return None

def save_radios(radios):
    """radios is a list of dictionaries"""
    with DBase() as cur:
        for radio in radios:
            radioId = radio['id']
            radioName = radio['name']
            radioUrl = radio['url']
            radioDef = radio['defRadio']
            #first try to UPDATE, if row exists it will be updated, else nothing happends
            cur.execute("UPDATE radios SET name=?, url=?, defRadio=? WHERE id=?;", (radioName, radioUrl, radioDef, radioId))
            #next try to INSERT, if row exists nothing happends, else new row is created
            #cur.execute("INSERT INTO radios VALUES(?, ?, ?, ?);", (radioId, radioName, radioUrl, radioDef))


def main():
    print("main()")
    NEW_RADIOS = [{ 'id': 1, 'name' : "deepthroat",\
            'url' :  "https://ch02.cdn.eurozet.pl/CHIDEP.mp3", 'defRadio' : False },
            { 'id' : 2, 'name' : "antyradio",\
            'url' :"http://an01.cdn.eurozet.pl/ant-waw.mp3", 'defRadio' : True },
            { 'id' : 3, 'name' : "eskarock",\
            'url' : "http://waw01-02.ic.smcdn.pl:8000/5380-1.aac.m3u", 'defRadio' : False },\
            { 'id' : 5, 'name' : "test",\
            'url' : "https://test.org", 'defRadio' : False }]
    create_empty_db()
    save_radios(DEF_RADIOS)
    add_sensor(DEF_SENSORS_LIST)
    #add_reading(2, 21.4)
    #for radio in get_radios().items():
    #    print(radio)
    #    print()
    #print("volume")
    #update_volume(0)
    #print(get_volume())


if __name__ == "__main__":
    main()
