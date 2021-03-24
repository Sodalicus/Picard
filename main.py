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
import sqlite3
from inout import talk_to_ard
from base import fake_temp
import os

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY='12345',
    DATABASE=os.path.join(app.root_path, 'data.db'),
    SITE_NAME='Remote Control'
))

usbPort = '/dev/ttyUSB0'
dataToSend = [b'1\n',b'2\n',b'3\n',b'4\n',b'5\n',b'6\b']
#talk_to_ard = fake_temp

def get_db():
    """Create connection to database """
    if not g.get('db'):
        con = sqlite3.connect(app.config['DATABASE'])
        con.row_factory = sqlite3.Row
        g.db = con
    return g.db

def retrive_data():
    """Get data from the base"""
    get_db()
    g.db.row_factory = sqlite3.Row
    cur = g.db.cursor()
    period = datetime('now', '-3 hours')
    sqlStatement = "SELECT * FROM reading WHERE time_added > datetime('now', '-1 hours');"
    cur.execute(sqlStatement)
    results = cur.fetchall()
    status = {'temp_ins0': [], 'temp_out0': [], 'datetime': []}
    for result in results:
        status['temp_ins0'].append(result['temp_ins0'])
        status['temp_out0'].append(result['temp_out0'])
        status['datetime'].append(result['time_added'])
    return status



@app.teardown_appcontext
def close_db(error):
    """Close connection to db"""
    if g.get('db'):
        g.db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    devices = [1,2,3,4]
    devStats = []
    status = talk_to_ard(usbPort,b'6\n')
    if status == 1:
        print("Arduino not connected")
    else:
        for i in range(4):
            devStats.append(status.split(":")[i])

    flash('Status: {}'.format(status))
    return render_template('index.html',data=zip(devices,devStats))

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

@app.route('/temp_graph', methods=["GET"])
def temp_graph():
    values = retrive_data()['temp_ins0']
    values2 = retrive_data()['temp_out0']
    labels = retrive_data()['datetime']

    return render_template('temp_graph.html', title='Temperature history', max=50, labels=labels, values=values, values2=values2)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
