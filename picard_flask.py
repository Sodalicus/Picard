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
from flask import jsonify
import os
import sqlite3
from picard_client import send
from picard_base import get_radios, save_radios, get_def_radio, get_recent_temp, get_now_playing
from picard_base import get_volume
from picard_lib import load_config

SETTINGS = load_config()
SSOCKET = (SETTINGS["SADDRESS"], SETTINGS["SPORT"])
SSOCKET = ("127.0.0.1", 65432)
CADDRESS = SETTINGS["CADDRESS"]
CPORT = SETTINGS["CPORT"]

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY='12345',
    DATABASE=os.path.join(app.root_path, 'data.db'),
    SITE_NAME='Remote Control'
))

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

def get_radios_names():
    radios = get_radios()
    namesList = []
    if radios == None: return None
    for radio in radios.values():
        if not (radio['name']) == None:
            namesList.append(radio['name'])
    return namesList

def get_channel_number(name):
    radios = get_radios()
    for radio in radios.items():
        if (radio[1]['name']) == name:
            return(radio[0])
    return None



@app.route('/', methods=['GET', 'POST'])
def index():
    """
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
    nowPlaying = "crap"
    #volume = player.return_volume()
    volume = "10"
    return render_template('index.html',\
            devices = devices,\
            mostRecent = mostRecent,\
            nowPlaying = nowPlaying,\
            volume = volume)
    """
    defRadio = get_def_radio()
    tempDate = get_recent_temp()
    radios = get_radios_names()

    nowPlaying = get_now_playing()
    volume = get_volume()
    if defRadio == None:
        defRadio = {'name' : 'No default radio selected', 'url' : '---'}
    return render_template('index.html',\
            defRadio = defRadio,\
            tempDate = tempDate,\
            radios = radios,\
            nowPlaying = nowPlaying,\
            volume = volume)

@app.route('/settings', methods=['GET'])
def settings():
    radios = get_radios()
    print('settings')
    print(radios)
    return render_template('settings.html',\
            radios = radios)

@app.route('/switch', methods=["POST"])
def switch():
    devNumber = int(request.form['dev_switch'])
    #talk_to_ard(devNumber-1)
    #flash('Clicked: {}'.format(devNumber))
    return redirect(url_for("index"))
    return render_template('index.html')


@app.route('/play_radio_def', methods=["POST"])
def play_radio_def():
    """Play default radio"""
    send("radio_def", SSOCKET)
    #player.play("radio")
    #display.msg("radio")
    return redirect(url_for("index"))

@app.route('/radio_stop', methods=["POST"])
def stop_radio():
    """Stop playing radio"""
    send("radio_stop", SSOCKET)
    #player.play("radio")
    #display.msg("radio")
    return redirect(url_for("index"))

@app.route('/noise', methods=["POST"])
def play_noise():
    #player.play("noise")
    #display.msg("noise")
    return redirect(url_for("index"))


@app.route('/beep', methods=['POST'])
def beep():
    #talk_to_ard(4)
    return redirect(url_for("index"))

@app.route('/volumeup', methods=['POST'])
def volume_up():
    send("volume_up", SSOCKET)
    return redirect(url_for("index"))

@app.route('/volumedown', methods=['POST'])
def volume_down():
    send("volume_down", SSOCKET)
    #player.volume_down()
    #vol = player.return_volume()
    #display.msg("Vol "+str(vol))
    return redirect(url_for("index"))

@app.route('/set_volume', methods=['POST'])
def set_volume():
    if request.method == 'POST':
        volume = request.get_json()
        print(volume)
        return jsonify(volume)


@app.route('/update_radios', methods=['POST'])
def update_radios():
    """Read the form from settings.html and update database accordingly."""
    if request.method == "POST":
        formData = request.form
        radioDef = int(request.form.get("radioDef"))
        radios = []
        for i in range(1, 11):
            radios.append( { 'id' :formData['radioId'+str(i)],\
                             'name' : formData['radioName'+str(i)],\
                             'url' : formData['radioUrl'+str(i)],\
                             'defRadio' : (True if radioDef == i else False)} )
        save_radios(radios)
        return redirect(url_for("settings"))

@app.route('/radio_play', methods=['POST'])
def radio_play():
    """get radio name from the drop-down input and play it."""
    if request.method == "POST":
        formData = request.form
        radioName =  formData['dropdown']
        radioChannel = get_channel_number(radioName)
        send(radioChannel, SSOCKET)
    return redirect(url_for("index"))

@app.route('/motion_light', methods=['POST'])
def motion_light():
    """make main app tell arduino to switch the state of the motion light."""
    if request.method == "POST":
        send("motion_light", SSOCKET)
    return redirect(url_for("index"))

@app.route('/night_light', methods=['POST'])
def night_light():
    """make main app tell arduino to switch the state of the night light."""
    if request.method == "POST":
        send("night_light", SSOCKET)
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True, host=CADDRESS, port=CPORT)
