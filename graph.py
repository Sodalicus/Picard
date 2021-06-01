#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Paweł Krzemiński 
#
# Distributed under terms of the MIT license.

"""

"""

def retrive_data(time0, time1):
    """Get data from the base between given dates"""
    cur = get_db().cursor()
    sqlQuery = "SELECT * FROM reading WHERE time_added BETWEEN (?) AND (?) ORDER BY time_added;"
    cur.execute(sqlQuery, (time0, time1))
    results = cur.fetchall()
    status = {'temp_ins0': [], 'temp_out0': [], 'time_added': []}
    for result in results:
        status['temp_ins0'].append(result['temp_ins0'])
        status['temp_out0'].append(result['temp_out0'])
        status['time_added'].append(result['time_added'])
    return status

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

