import pandas as pd
import psycopg2
import os
from flask import Flask, Blueprint, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


views = Blueprint('views', __name__)

@views.route('/')
def home():
    session = db_connect()
    
    df_listings = pd.read_sql("""
                        select count(*) AS listings
                        from listings
                    """, session.connection())
    listings = df_listings['listings'].item()
    
    df_makes = pd.read_sql("""
                        select count(*) AS makes
                        from makes
                    """, session.connection())
    makes = df_makes['makes'].item()
    
    df_models = pd.read_sql("""
                        select count(*) AS models
                        from models
                    """, session.connection())
    models = df_models['models'].item()

    session.close()
    return render_template('home.html', listings=listings, makes=makes, models=models)

@views.route('/chart')
def draw_chart():
    session = db_connect()
    
    df = pd.read_sql("""
                        select extract(year from completion_date) AS auctionyear,
                        percentile_cont(0.50) within group (order by price) as price
                        from listings
                        where make = 'Porsche' and status = 'Sold' and model_name = 'Porsche 911 GT3'
                        group by make, auctionyear
                        order by auctionyear ASC
                    """, session.connection())

    model_name = 'Porsche 911 GT3'
    auctionyear = df['auctionyear'].astype(int).values.tolist() # x-axis
    price = df['price'].values.astype(int).tolist() # y-axis

    session.close()
    return render_template('chart.html', model_name=model_name, auctionyear=auctionyear, price=price)

def db_connect():
    DATABASE_URI = os.getenv("DATABASE_URI")
    engine = create_engine(DATABASE_URI)
    connection = scoped_session(sessionmaker(bind=engine))
    return connection