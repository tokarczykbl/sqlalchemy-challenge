# Import the dependencies.
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

# Create a session
session = Session(engine)

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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/mm-dd-yyyy<br/>"
        f"/api/v1.0/mm-dd-yyyy/mm-dd-yyyy"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago)
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)     
   

@app.route("/api/v1.0/stations")
def station():
    placeholder = 1
    return f"Something"


@app.route("/api/v1.0/tobs")
def tobs():
    placeholder = 1
    return f"Something"

    
if __name__ == "__main__":
    app.run(debug=True)