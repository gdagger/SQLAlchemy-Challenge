# Import dependencies

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session link to database
session = Session(engine)



#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################


### Homepage Route
@app.route("/")

def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/gettobs/&lt;start_date&gt;<br>"
        f"/api/v1.0/gettobs/&lt;start_date&gt;/&lt;end_date&gt;"
    )

### Precipitation Route
@app.route("/api/v1.0/precipitation")

def precipitation():
    """Retrieve JSON representation of precipitation data for previous year"""
    results = session.query(Measurement.date,Measurement.prcp).\
                        filter(Measurement.date >= '2016-08-23').\
                        all()
    # Close session
    session.close()

    # List comprehension to create list of dictionaries (date:prcp) from the row data 
    all_precip = [{date: prcp} for date, prcp in results]

    return jsonify(all_precip)



### Stations Route
@app.route("/api/v1.0/stations")

def stations():
    """Return JSON list of stations"""
    results = session.query(Station.station).all()
    
    # Close session
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


### Tobs Route
@app.route("/api/v1.0/tobs")

def tobs():
    """Return JSON list of tobs for previous year"""

    #Query most past year of tobs data from most active station
    results = session.query(Measurement.tobs).\
                    filter(Measurement.station == 'USC00519281').\
                    filter(Measurement.date >= '2016-08-23').all()
    
    # Close session
    session.close()

    # Convert list of tuples into normal list
    tobs_past_year = list(np.ravel(results))

    

    return jsonify(tobs_past_year)




### Start/End Date Route
@app.route("/api/v1.0/gettobs/<start>")
@app.route("/api/v1.0/gettobs/<start>/<end>")

def start_end_date(start, end='2017-08-23'):
    """Return JSON list of min/avg/max temp between given start and end dates"""

    # Create list of one tuple containing min, max, avg tobs for date range
    results = session.query(func.min(Measurement.tobs), \
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        filter(Measurement.date <= end).all()
    
    tobs_list = []
    for tmin, tmax, tavg in results:
        tobs_dict = {}
        tobs_dict["TMIN"] = tmin
        tobs_dict["TMAX"] = tmax
        tobs_dict["TAVG"] = round(tavg,2)
        tobs_list.append(tobs_dict)

    # Close session
    session.close()

    return jsonify(tobs_list)


if __name__ == "__main__":
    app.run(debug=True)