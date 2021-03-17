# Import Flask
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from numpy import mean

from flask import Flask, jsonify

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB

# Create an app
app = Flask(__name__)

@app.route("/")
def home():
    return (
        f'Welcome to the Hawaii Weather API! <br>'
        f'<br/>'
        f'Here are the available routes: <br/>'
        f'<br/>'
        f'/api/v1.0/precipitation <br/>'
        f'/api/v1.0/stations <br/>'
        f'/api/v1.0/tobs <br/>'
        f'<br/>'
        f'For the following paths, enter a date using YYYY-mm-dd format in place of "start" and "end" to filter a date range. And end date is not required.<br/>'
        f'<br/>'
        f'/api/v1.0/start <br/>'
        f'/api/v1.0/start/end <br/>'
    )

# Make routes
@app.route('/api/v1.0/precipitation')
def precipitation():

    session = Session(engine)

    last_date = session.query(measurement.date).\
        order_by(measurement.date.desc()).\
        first()

    last_date = last_date[0]
    last_date = last_date.split('-')

    first_date = dt.date(int(last_date[0]),
        int(last_date[1]),
        int(last_date[2])) - dt.timedelta(days=365)

    measurement_results = session.query(measurement.date, func.max(measurement.prcp)).\
        filter(measurement.date >= first_date).\
        group_by(measurement.date).\
        order_by(measurement.date.asc()).all()

    session.close()

    precip_json = []
    for date, prcp in measurement_results:
        precip_dict = {}
        precip_dict['date'] = date
        precip_dict['prcp'] = prcp
        precip_json.append(precip_dict)

    return jsonify(precip_json)


@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    station_results = session.query(station.station).all()
    
    session.close()

    all_stations = list(np.ravel(station_results))

    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def tobs():

    session = Session(engine)

    station_freq = session.query(func.count(measurement.tobs), measurement.station).\
        group_by(measurement.station).\
        order_by(desc(func.count(measurement.tobs))).all()

    session.close()

    most_active_station = station_freq[0][1]

    session = Session(engine)

    active_last_date = session.query(measurement.date).\
        order_by(measurement.date.desc()).\
        filter(measurement.station == most_active_station).first()

    session.close()

    active_last_date
    active_last_date = active_last_date[0]
    active_last_date = active_last_date.split('-')

    active_first_date = dt.date(int(active_last_date[0]),
        int(active_last_date[1]),
        int(active_last_date[2])) - dt.timedelta(days=365)

    session = Session(engine)

    active_measurement_results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= active_first_date).\
        filter(measurement.station == most_active_station)

    session.close()

    tobs_json = []
    for date, tobs in active_measurement_results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_json.append(tobs_dict)

    return jsonify(tobs_json)

@app.route('/api/v1.0/<start>')
def start(start):

    start_search = start

    session = Session(engine)

    tobs_results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= start_search)

    session.close()

    tobs_list = []
    for temp in tobs_results:
            tobs_list.append(temp.tobs)

    max_temp = max(tobs_list)
    min_temp = min(tobs_list)
    avg_temp = round(mean(tobs_list), 2)

    result_dict = {'Max': max_temp, 'Min': min_temp, 'Avg': avg_temp}

    return (result_dict)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):

    start_search = start
    end_search = end

    if start_search > end_search:
        return jsonify({'error': f'START DATE must be before END DATE'})

    session = Session(engine)

    tobs_results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= start_search).\
        filter(measurement.date <= end_search)

    session.close()

    tobs_list = []
    for temp in tobs_results:
            tobs_list.append(temp.tobs)

    max_temp = max(tobs_list)
    min_temp = min(tobs_list)
    avg_temp = round(mean(tobs_list), 2)

    result_dict = {'Max': max_temp, 'Min': min_temp, 'Avg': avg_temp}

    return (result_dict)

if __name__ == "__main__":
    app.run(debug=True)