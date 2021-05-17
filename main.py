#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Sodalicus
#
# Distributed under terms of the MIT license.

"""

"""

from flask import Flask, g
from flask import render_template, request, redirect, url_for, flash
from flask import session 
import sqlite3
from inout import talk_to_ard
import os
import time
import datetime


app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY='12345',
    DATABASE=os.path.join(app.root_path, 'data.db'),
    SITE_NAME='Remote Control'
))

usbPort = '/dev/ttyUSB0'
dataToSend = [b'1\n',b'2\n',b'3\n',b'4\n',b'5\n',b'6\b']

def get_db():
    """Create connection to database """
    if not g.get('db'):
        con = sqlite3.connect(app.config['DATABASE'])
        con.row_factory = sqlite3.Row
        g.db = con
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close connection to db"""
    if g.get('db'):
        g.db.close()


def retrive_data(time0, time1):
    """Get data from the base"""
    cur = get_db.cursor()
    sqlQuery = "SELECT * FROM reading WHERE time_added BETWEEN (?) AND (?) ORDER BY time_added;"
    cur.execute(sqlQuery, (time0, time1))
    results = cur.fetchall()
    status = {'temp_ins0': [], 'temp_out0': [], 'time_added': []}
    for result in results:
        status['temp_ins0'].append(result['temp_ins0'])
        status['temp_out0'].append(result['temp_out0'])
        status['time_added'].append(result['time_added'])
    return status



def read_devices_info():
    """Read device info (name, type, switchability, description)
       from table device"""
    cur = get_db().cursor()
    sqlQuery = "SELECT * FROM device;"
    cur.execute(sqlQuery)
    results = cur.fetchall()
    devices = []
    for row in results:
        devices.append(dict((cur.description[idx][0], value)
                for idx, value in enumerate(row)))
    return devices




@app.route('/', methods=['GET', 'POST'])
def index():
    devices = read_devices_info()
    status = talk_to_ard(usbPort,b'6\n')
    if status == 1:
        print("Arduino not connected")
        status = [0]*9
    for device in devices:
        device['status'] = status[device['id']-1]
    print(devices)

    flash('Status: {}'.format(status))
    return render_template('index.html',devices = devices)

@app.route('/beep', methods=['POST'])
def beep():
    talk_to_ard(usbPort, dataToSend[4])
    return redirect(url_for("index"))
    return render_template('index.html')

@app.route('/switch', methods=["POST"])
def switch():
    devNumber = int(request.form['dev_switch'])
    talk_to_ard(usbPort, dataToSend[devNumber-1])
    flash('Clicked: {}'.format(devNumber))
    return redirect(url_for("index"))
    return render_template('index.html')

@app.route('/temp_graph', methods=["GET", "POST"])
def temp_graph():
    if request.method == "POST":
        time0 = request.form['time0']
        time1 = request.form['time1']
        values = retrive_data(time0, time1)['temp_ins0']
        values2 = retrive_data(time0, time1)['temp_out0']
        labels = retrive_data(time0, time1)['time_added']
        return render_template('temp_graph.html', title='Temperature history', max=50, labels=labels, values=values, values2=values2, time0=time0, time1=time1)
    else:
        time0 = (datetime.datetime.now()-datetime.timedelta(1)).strftime("%Y-%m-%d")
        time1 = datetime.datetime.now().strftime("%Y-%m-%d")
        print(time0)
        print(time1)
        values = retrive_data(time0, time1)['temp_ins0']
        values2 = retrive_data(time0, time1)['temp_out0']
        labels = retrive_data(time0, time1)['time_added']

        return render_template('temp_graph.html', title='Temperature history', max=50, labels=labels, values=values, values2=values2, time0=time0, time1=time1)

@app.route('/noise', methods=["POST"])
def play_noise():
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
