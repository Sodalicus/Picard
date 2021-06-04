#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Paweł Krzemiński 
#
# Distributed under terms of the MIT license.

"""

"""

from flask import Flask, g
from flask import render_template, request, redirect, url_for, flash
from flask import session
import os
import sqlite3
from ard import talk_to_ard
from radio import MPlayer


app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY='12345',
    DATABASE=os.path.join(app.root_path, 'data.db'),
    SITE_NAME='Remote Control'
))

player = MPlayer()

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


def retrive_data():
    """Get most recent reading from database"""
    cur = get_db().cursor()
    sqlQuery = "SELECT * FROM reading ORDER BY time_added ASC;"
    cur.execute(sqlQuery)
    results = cur.fetchone()
    return results


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
    status = retrive_data()
    if status == None:
        status = [0]*11
    for device in devices:
        device['status'] = status[device['id']]
        if device['unit'] == "celsius":
            device['symbol'] = "&#8451;"
        elif device['unit'] == "percents":
            device['symbol'] = "%"
        elif device['unit'] == "minutes":
            device['symbol'] = "&prime;"
        else:
            device['symbol'] = None
    mostRecent = status[10]
    #flash('Status: {}'.format(status))
    nowPlaying = player.now_playing()
    volume = player.return_volume()
    return render_template('index.html',\
            devices = devices,\
            mostRecent = mostRecent,\
            nowPlaying = nowPlaying,\
            volume = volume)


@app.route('/switch', methods=["POST"])
def switch():
    devNumber = int(request.form['dev_switch'])
    talk_to_ard(devNumber-1)
    #flash('Clicked: {}'.format(devNumber))
    return redirect(url_for("index"))
    return render_template('index.html')


@app.route('/radio', methods=["POST"])
def play_radio():
    player.play("radio")
    return redirect(url_for("index"))

@app.route('/noise', methods=["POST"])
def play_noise():
    player.play("noise")
    return redirect(url_for("index"))


@app.route('/beep', methods=['POST'])
def beep():
    talk_to_ard(4)
    return redirect(url_for("index"))

@app.route('/volumeup', methods=['POST'])
def volume_up():
    player.volume_up()
    return redirect(url_for("index"))

@app.route('/volumedown', methods=['POST'])
def volume_down():
    player.volume_down()
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
