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
dataToSend = b'1\n'
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
    devices = ["Device#01", "Device#02", "Device#03", "Device#04"]
    dev_stats = ["on", "off", "on", "off"]
    ledState = talk_to_ard(usbPort,b'3\n')
    flash('The LED is now: {}'.format(ledState))
    return render_template('index.html', ledState=ledState, data=zip(devices,dev_stats))

@app.route('/beep', methods=['POST'])
def beep():
    talk_to_ard(usbPort, b'2\n')
    return redirect(url_for("index"))
    return render_template('index.html')

@app.route('/switch', methods=["POST"])
def switch():
    talk_to_ard(usbPort, dataToSend)
    return redirect(url_for("index"))
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
