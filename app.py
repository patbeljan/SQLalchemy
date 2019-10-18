from flask import Flask, jsonify, request
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker
#from climate_queries import calc_temps
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

def calc_temps(start_date, end_date):
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Precipitation data page- /api/v1.0/precipitation "
        f"Station data page- /api/v1.0/stations "
        f"Temperature data page- /api/v1.0/tobs "
        f"page- /api/v1.0/start?arg1=<start> "
        f"page- /api/v1.0/start_end?arg1=<start>arg2=<end> ")


@app.route("/api/v1.0/precipitation")
def precipitation():
    df = pd.read_sql_query('SELECT m.date, SUM(m.prcp) as Total_prcp FROM measurement as m GROUP BY m.date ORDER BY m.date',con = engine)
    mydict = df.set_index('date').T.to_dict('list')

    return jsonify(mydict)

@app.route("/api/v1.0/stations")
def stations():
    df1 = pd.read_sql_query('SELECT DISTINCT s.station FROM station as s', con = engine)
    mydict = df1.to_dict('list')
    return jsonify(mydict)

@app.route("/api/v1.0/tobs")
def tobs():
    df2 = pd.read_sql_query('SELECT date, tobs FROM measurement', con = engine)
    last_date = pd.to_datetime(df2.iloc[-1, 0])
    date = last_date - relativedelta(years=1)
    x = str(date)
    y = x.split(' ')
    df3 = pd.read_sql_query(f'SELECT m.date, m.tobs From measurement as m WHERE m.date >= "{y[0]}"', con = engine)
    mydict = df3.set_index('date').T.to_dict('list')
    return jsonify(mydict)

# Must restart kernel after using either of these api pages
@app.route("/api/v1.0/start")
def start():
    arg1 = request.args['arg1']
    #print(arg1)
    #print('hello')
    list_set = None
    list_set = calc_temps(arg1, arg1)
    return jsonify(list_set)

# Must restart kernel after using either of these api pages
@app.route("/api/v1.0/start_end")
def period():
    arg1 = request.args['arg1']
    arg2 = request.args['arg2']
    list_set2 = None
    list_set2 = calc_temps(arg1,arg2)
    return jsonify(list_set2)


if __name__ == "__main__":
    # @TODO: Create your app.run statement here
    app.run(debug = True)

