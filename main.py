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
import os

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY='12345',
    DATABASE=os.path.join(app.root_path, 'data.db'),
    SITE_NAME='Remote Control'
))

usbPort = '/dev/ttyUSB0'
dataToSend = [b'1\n',b'2\n',b'3\n',b'4\n',b'5\n',b'6\b']
ledState = 0

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

@app.route('/', methods=['GET', 'POST'])
def index():
    devices = [1,2,3,4]
    devStats = []
    status = talk_to_ard(usbPort,b'6\n')
    for i in range(2):
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
