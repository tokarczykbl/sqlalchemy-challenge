# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to my homepage! Please see available listed routes below.<br/><br/> "
        f"&emsp;To view date and precipitation information:&emsp;&emsp;&emsp;&emsp;/api/v1.0/precipitation<br/>"
        f"&emsp;To view a list of weather stations:&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;/api/v1.0/stations<br/>"
        f"&emsp;To view the most active station's recent year's data:&emsp;/api/v1.0/tobs<br/>"
        f"<br>"
        f"For dynamic date entries use YYYY-MM-DD formating<br/>"
        f"<br>"
        f"&emsp;To find stats from the start date to end of data set: &emsp; /api/v1.0/&lt;start&gt;<br/>"
        f"&emsp;To find stats for a specified period of time: &emsp;&emsp;&emsp;&emsp;/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
   )


@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB       
    session = Session(engine)
    
    # Querying DB to find the max date in the Measurement table
    max_date_row = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    
    # Extracting date string from the row
    max_date = max_date_row[0]
    
    # Converting string to date format for date calculation
    convert_date = datetime.strptime(max_date, '%Y-%m-%d')
    year_ago = convert_date - dt.timedelta(days=365)
    
    # Querying database to find date and precipitation values for the most recent year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago)
    
    # Creating dictionary from query results
    precip_data = {date: prcp for date, prcp in precipitation}
    
    # Closing session
    session.close()
    
    # Printing results
    return jsonify(precip_data)


@app.route("/api/v1.0/stations")
def station():
    
    # Create our session (link) from Python to the DB       
    session = Session(engine)
    
    # Querying Station table to get list of all stations
    stations_query = session.query(Station.station).all()
    
    # Converting the result into a list of station anmes
    station_list = list(np.ravel(stations_query))
    
    # Closing session
    session.close()
    
    # Printing list of stations
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB       
    session = Session(engine)
            
    # Finding the most active station and storing it in a variable
    most_active_station = session.query(Measurement.station, func.count(Measurement.station).label("station_count")).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()
    
    # Finding the most recent date for the most active sation
    max_date = session.query(func.max(Measurement.date)).\
        filter(Measurement.station == most_active_station[0]).scalar()
           
    # Converting string to date format for date calculation
    convert_date = datetime.strptime(max_date, '%Y-%m-%d')
    year_ago = convert_date - dt.timedelta(days=365)
    
    # Querying the database to find temperature observations for the most active station in the past year
    most_active_past_year = session.query(Measurement.tobs).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.station == most_active_station[0]).all()
    
    # Creating list from query results
    most_active_temp_list = [tobs[0] for tobs in most_active_past_year]
    
    # Closing session
    session.close()
    
    # Returning temperature observations for the most active station in the past year as a JSON response
    return jsonify (most_active_temp_list)

    
@app.route("/api/v1.0/<start>")
def open_stats(start):
    # Create our session (link) from Python to the DB       
    session = Session(engine)
    
    # List for querying min, average and max temperatures
    sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Querying session based on start date selected
    open_stats = session.query(*sel).\
        filter(Measurement.date >= start).all()
    
    for min, avg, max in open_stats:
        open_stats_dict = {}
        open_stats_dict["Min"] = min
        open_stats_dict["Average"] = avg
        open_stats_dict["Max"] = max
    
    # Closing session
    session.close()
    
    # Returning temperature observations for open date range from specified start as a JSON response
    return jsonify(open_stats_dict)

@app.route("/api/v1.0/<start>/<end>")
def open_close_stats(start, end):
    # Create our session (link) from Python to the DB       
    session = Session(engine)
    
    # List for querying min, average and max temperatures
    sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Querying session based on start and end dates selected
    open_close_stats = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    # Creating dictionary from query results
    for min, avg, max in open_close_stats:
        open_close_stats_dict = {}
        open_close_stats_dict["Min"] = min
        open_close_stats_dict["Average"] = avg
        open_close_stats_dict["Max"] = max
    
    # Closing session
    session.close()
    
    # Returning temperature observations for closed date range from specified start and end as a JSON response
    return jsonify(open_close_stats_dict)

if __name__ == "__main__":
    app.run(debug=True)