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
engine = create_engine('sqlite:///hawaii.sqlite')

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

# Main page
@app.route('/')
def home():
    return (
        f'Welcome to the Hawaii Weather API! <br>'
        f'<br/>'
        f'Here are the available routes: <br/>'
        f'<br/>'
        f'/api/v1.0/precipitation <br/>'
        f'/api/v1.0/stations <br/>'
        f'<br/>'
        f"The following route will return a year's worth of temperature observation (TOBS) data from the most active station in Hawaii. <br/>"
        f'<br/>'
        f'/api/v1.0/tobs <br/>'
        f'<br/>'
        f'For the following routes, enter a date using YYYY-mm-dd format in place of "start_date" and "end_date" to filter a date range. An end date is not required.<br/>'
        f'<br/>'
        f'/api/v1.0/start_date <br/>'
        f'/api/v1.0/start_date/end_date <br/>'
    )

# Make precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():

    session = Session(engine)

    # Query measurement data to find last date
    last_date = session.query(measurement.date).\
        order_by(measurement.date.desc()).\
        first()

    # Extract date from result list
    last_date = last_date[0]
    # Split string by delimiter into list
    last_date = last_date.split('-')

    # Pass last_date list into dt.date and find 12 months (365 days) before last date
    first_date = dt.date(int(last_date[0]),
        int(last_date[1]),
        int(last_date[2])) - dt.timedelta(days=365)

    # Query measurement data using first date filter
    measurement_results = session.query(measurement.date, func.max(measurement.prcp)).\
        filter(measurement.date >= first_date).\
        group_by(measurement.date).\
        order_by(measurement.date.asc()).all()

    session.close()

    # Build json with results
    precip_json = []
    for date, prcp in measurement_results:
        precip_dict = {}
        precip_dict['date'] = date
        precip_dict['prcp'] = prcp
        precip_json.append(precip_dict)

    return jsonify(precip_json)

# Make stations route
@app.route('/api/v1.0/stations')
def stations():

    session = Session(engine)

    # Query station data
    station_results = session.query(station.station).all()
    
    session.close()

    # Make list of results
    all_stations = list(np.ravel(station_results))

    return jsonify(all_stations)

# Make tobs route
@app.route('/api/v1.0/tobs')
def tobs():

    session = Session(engine)

    # Query measurement data
    station_freq = session.query(func.count(measurement.tobs), measurement.station).\
        group_by(measurement.station).\
        order_by(desc(func.count(measurement.tobs))).all()

    session.close()

    # Extract most most active station from result
    most_active_station = station_freq[0][1]

    session = Session(engine)

    # Find last measurement of most active station
    active_last_date = session.query(measurement.date).\
        order_by(measurement.date.desc()).\
        filter(measurement.station == most_active_station).first()

    session.close()

    # Extract date from list
    active_last_date = active_last_date[0]
    # Split string by delimiter into list
    active_last_date = active_last_date.split('-')

    # Pass last_date list into dt.date and find 12 months (365 days) before last date
    active_first_date = dt.date(int(active_last_date[0]),
        int(active_last_date[1]),
        int(active_last_date[2])) - dt.timedelta(days=365)

    session = Session(engine)

    # Query measurement data using first date filter
    active_measurement_results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= active_first_date).\
        filter(measurement.station == most_active_station)

    session.close()

    # Build json with results
    tobs_json = []
    for date, tobs in active_measurement_results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_json.append(tobs_dict)

    return jsonify(tobs_json)

@app.route('/api/v1.0/<start>')
def start(start):

    # make variable to pass into function
    start_search = start

    session = Session(engine)

    # Query measurement data using start search
    tobs_results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= start_search)

    session.close()

    # Make list from from results
    tobs_list = []
    for temp in tobs_results:
            tobs_list.append(temp.tobs)

    # Find max, min, and avg from list
    max_temp = max(tobs_list)
    min_temp = min(tobs_list)
    avg_temp = round(mean(tobs_list), 2)

    # Make dictionary using variables
    result_dict = {'Max': max_temp, 'Min': min_temp, 'Avg': avg_temp}

    return jsonify(result_dict)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):

    # make variables to pass into function
    start_search = start
    end_search = end

    # create error message in case start date is after end date
    if start_search > end_search:
        return jsonify({'error': f'No results. START DATE must be before END DATE'})

    session = Session(engine)

    # Query measurement data using start and end search
    tobs_results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= start_search).\
        filter(measurement.date <= end_search)

    session.close()

    # Make list from from results
    tobs_list = []
    for temp in tobs_results:
            tobs_list.append(temp.tobs)

    # Find max, min, and avg from list
    max_temp = max(tobs_list)
    min_temp = min(tobs_list)
    avg_temp = round(mean(tobs_list), 2)

    # Make dictionary using variables
    result_dict = {'Max': max_temp, 'Min': min_temp, 'Avg': avg_temp}

    return jsonify(result_dict)

if __name__ == '__main__':
    app.run(debug=True)