import pandas as pd
import psycopg2
import os
from flask import Flask, Blueprint, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


views = Blueprint('views', __name__)

@views.route('/')
def home():
    session = db_connect()
    
    df_listings = pd.read_sql("""
                        SELECT COUNT(*) AS listings
                        FROM listings
                    """, session.connection())
    listings = df_listings['listings'].item()
    
    df_makes = pd.read_sql("""
                        SELECT COUNT(*) AS makes
                        FROM makes
                    """, session.connection())
    makes = df_makes['makes'].item()
    
    df_models = pd.read_sql("""
                        SELECT COUNT(*) AS models
                        FROM models
                    """, session.connection())
    models = df_models['models'].item()
    
    df_listing_data = pd.read_sql("""
                        SELECT makes.make, COUNT(*) FROM listings
                        INNER JOIN makes ON listings.make = makes.make
                        GROUP BY makes.make_id ORDER BY make ASC
                    """, session.connection())

    session.close()
    return render_template('home.html', listings=listings, makes=makes, models=models, df_listing_data=df_listing_data)

@views.route('/chart')
def draw_chart():
    session = db_connect()
    make = request.args.get('make')
    
    df = pd.read_sql("""
                        select extract(year from completion_date) AS auctionyear,
                        count(*) as listingcount,
                        percentile_cont(0.50) within group (order by price) as price
                        from listings
                        where make = '%s' and status = 'Sold' and extract(year from completion_date) <> 2014
                        group by make, auctionyear
                        order by auctionyear ASC
                    """ % make, session.connection())

    auctionyear = df['auctionyear'].astype(int).values.tolist() # chart x-axis
    price = df['price'].values.astype(int).tolist() # chart y-axis
    supporting_data = df.reset_index()[['auctionyear', 'listingcount']].values.astype(int).tolist()

    session.close()
    return render_template('chart.html', make=make, auctionyear=auctionyear, price=price, supporting_data=supporting_data)

def db_connect():
    DATABASE_URI = os.getenv("DATABASE_URI")
    engine = create_engine(DATABASE_URI)
    connection = scoped_session(sessionmaker(bind=engine))
    return connection