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
from picard_base import get_radios2, save_radios, get_recent_temp, get_now_playing
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

@app.route('/', methods=['GET', 'POST'])
def index():
    tempDate = get_recent_temp()
    radios = get_radios2()

    nowPlaying = get_now_playing()
    volume = get_volume()
    return render_template('index.html',\
            tempDate = tempDate,\
            radios = radios,\
            nowPlaying = nowPlaying,\
            volume = volume)

@app.route('/settings', methods=['GET'])
def settings():
    radios = get_radios2()
    return render_template('settings.html',\
            radios = radios)

@app.route('/switch', methods=["POST"])
def switch():
    devNumber = int(request.form['dev_switch'])
    return redirect(url_for("index"))
    return render_template('index.html')

@app.route('/radio_stop', methods=["POST"])
def stop_radio():
    """Stop playing radio"""
    send("radio stop", SSOCKET)
    return redirect(url_for("index"))

@app.route('/beep', methods=['POST'])
def beep():
    return redirect(url_for("index"))

@app.route('/volumeup', methods=['POST'])
def volume_up():
    send("volume +", SSOCKET)
    return redirect(url_for("index"))

@app.route('/volumedown', methods=['POST'])
def volume_down():
    send("volume -", SSOCKET)
    #player.volume_down()
    #vol = player.return_volume()
    #display.msg("Vol "+str(vol))
    return redirect(url_for("index"))

@app.route('/set_volume', methods=['POST'])
def set_volume():
    if request.method == 'POST':
        volume = request.get_json()
        send("volume {}".format(volume), SSOCKET)
        return(jsonify("response:volume:"+str(volume)))

@app.route('/message', methods=['POST', 'GET'])
def message():
    #msg = request.get_json()
    msg = request.content_type
    return(jsonify("OK"))

@app.route('/update_radios', methods=['POST'])
def update_radios():
    """Read the form from settings.html and update database accordingly."""
    if request.method == "POST":
        formData = request.form
        radioNames = formData.getlist("radioName")
        radioUrls = formData.getlist("radioUrl")
        radios = []
        for i in range(0, 9):
            radios.append( { 'id' : str(i+1),\
                             'name' : radioNames[i],\
                             'url' : radioUrls[i] })
        save_radios(radios)
        return redirect(url_for("settings"))

@app.route('/play_channel', methods=['POST'])
def play_channel():
    """get radio name from the drop-down input and play it."""
    type = None
    if request.method == "POST":
        if request.is_json == True:
            """ request sent by js button 'Content-type: application/json' """
            type = "json"
            req = request.json.split()
            if len(req) == 2:
                radioChannel = req[1]

        else:
            """ request sent by <form> """
            type = "form"
            formData = request.form
            radioChannel =  formData['channel']

        try:
            """check if radioChannel is and int and lower than 200"""
            radioChannel = int(radioChannel)
            if radioChannel <= 200:
                radioChannel = "channel "+str(radioChannel)
                send(radioChannel, SSOCKET)
        except ValueError:
            print("Not a valid channel number, must be an int.")
        if type == "json":
            return jsonify("response::"+radioChannel)
        elif type == "form":
            return redirect(url_for("index"))


@app.route('/motion_light', methods=['POST'])
def motion_light():
    """make main app tell arduino to switch the state of the motion light."""
    if request.method == "POST":
        send("lamp motion", SSOCKET)
    return redirect(url_for("index"))

@app.route('/night_light', methods=['POST'])
def night_light():
    """make main app tell arduino to switch the state of the night light."""
    if request.method == "POST":
        send("lamp turn", SSOCKET)
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True, host=CADDRESS, port=CPORT)
