### import dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

if __name__ ==  '__main__':
    app.run(debug=True)

### Connection to Hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflecting database into nre model
Base = automap_base()

# Reflecting table
Base.prepare(engine, reflect = True)

# Measurement and Station refrences
Measurement = Base.classes.measurement
Station = Base.classes.station

### Flask
app = Flask(__name__)

@app.route("/")
def welcome():
    """List api routes."""
    return(f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Note: To access values between start_date and end_date enter dates using 'YYYY-MM-DD' "
        )

### Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    """Return a list of precipitation (prcp) and date (date) data"""

    precip_results = session.query(Measurement.prcp, Measurement.date).all()

    session.close()

    precip_values = []
    for prcp, date in precip_results:
        precip_dict = {}
        precip_dict["precipitation"] = prcp
        precip_dict["date"] = date
        precip_values.append(precip_dict)
    return jsonify(precip_values)

### Stations
@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    """Return a list of Stations from database"""

    station_results = session.query(Station.station, Station.id).all()

    session.close()    

    station_values = []
    for station, id in station_results:
        station_values_dict = {}
        station_values_dict['station'] = station
        station_values_dict['id'] = id
        station_values.append(station_values_dict)
    return jsonify (station_values)


### Tobs
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    """Return data for the most active station within the last year"""

    last_query = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    print(last_query)

last_query_values = []
for date in last_query:
    last_dict = {}
    last_dict["date"] = date
    last_query_values.append(last_dict)
print(last_query_values)

start_date = dt.date(2017, 8, 23)-dt.timedelta(days=365)
print(start_date)

active_station = session.query(Measurement.station, func.count(Measurement.station)).\
    order_by(func.count(Measurement.station).desc()).\
    group_by(Measurement.station).frst()
most_active_station = active_station[0]

session.close()

print(most_active_station)

last_tobs = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
filter(Measurement.date > start_date).\
filter(Measurement.station == most_active_station)

## JSON tobs
last_tobs_values = []
for date, tobs, station in last_tobs:
    tobs_dict = {}
    tobs_dict["date"] = date
    tobs_dict["tobs"] = tobs
    tobs_dict["station"] = station
    last_tobs_values.append(tobs_dict)

    return jsonify(last_tobs_values)



### Start / End
@app.route('/api/v1.0/<start>', defaults = {'end': None})
@app.route("/api/v1.0/<start>/<end>")
def temps_date_range(start, end):

    session = Session(engine)

    if end != None:
        temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        
    else:
        temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

session.close()

temp_list = []
no_temp = False
for min_temp, avg_temp, max_temp in temp_data:
    if min_temp == None or avg_temp == None or max_temp == None:
        no_temp = True
    temp_list.append(min_temp)
    temp_list.append(max_temp)
    temp_list.append(avg_temp)

if no_temp == True:
    return f"No data exists in this range, try another."
else:
    return jsonify(temp_list)
