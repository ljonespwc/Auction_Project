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
                        SELECT TO_CHAR(completion_date, 'YYYY-MM') AS auctionperiod,
                        count(*) AS listingcount,
                        percentile_cont(0.50) WITHIN GROUP (ORDER BY price) AS price
                        FROM listings
                        WHERE status = 'Sold' AND EXTRACT(year from completion_date) > 2015
                        GROUP BY auctionperiod
                        ORDER BY auctionperiod ASC
                    """, session.connection())

    auctionperiod = df_listing_data['auctionperiod'].values.tolist() # chart x-axis
    price = df_listing_data['price'].values.astype(int).tolist() # chart y-axis
    listingcount = df_listing_data['listingcount'].values.astype(int).tolist() # chart tooltips

    session.close()
    return render_template('home.html', listings=listings, makes=makes, models=models,
                           auctionperiod=auctionperiod, price=price, listingcount=listingcount)

@views.route('/makes')
def list_makes():
    session = db_connect()
    
    df_listing_data = pd.read_sql("""
                        SELECT makes.make, COUNT(*) FROM listings
                        INNER JOIN makes ON listings.make = makes.make
                        GROUP BY makes.make_id ORDER BY make ASC
                    """, session.connection())

    session.close()
    return render_template('makes.html', df_listing_data=df_listing_data)

@views.route('/chart')
def draw_chart():
    session = db_connect()
    
    make = request.args.get('make')
    df_dropdown = pd.read_sql("""
                            SELECT DISTINCT model_name
                            FROM models INNER JOIN makes ON models.make_id = makes.make_id
                            WHERE makes.make = '%s'
                            ORDER BY model_name ASC
                            """ % make, session.connection())
    dropdown_data = df_dropdown.reset_index()['model_name'].values.tolist()
    
    df_models_num = pd.read_sql("""
                        SELECT COUNT(*) AS models
                        FROM models
                    """, session.connection())
    models_num = df_models_num['models'].item()
    
    if not request.args.get('model'): # if make is selected from home page, show make data
        
        df = pd.read_sql("""
                            select extract(year from completion_date) AS auctionyear,
                            count(*) as listingcount,
                            percentile_cont(0.50) within group (order by price) as price
                            from listings
                            where make = '%s' and status = 'Sold' and extract(year from completion_date) > 2015
                            group by make, auctionyear
                            order by auctionyear ASC
                        """ % make, session.connection())

        listings_by_year = df['listingcount'].values.astype(int).tolist()
        auctionyear = df['auctionyear'].astype(int).values.tolist() # chart x-axis
        price = df['price'].values.astype(int).tolist() # chart y-axis
        supporting_data = df.reset_index()[['auctionyear', 'listingcount']].values.astype(int).tolist()
        
        session.close()
        return render_template('chart.html', make=make, auctionyear=auctionyear, price=price,
                               supporting_data=supporting_data, dropdown_data=dropdown_data,
                               listings_by_year=listings_by_year)
    
    else: # if model is selected from dropdown on chart page, show model data

        model = request.args.get('model')
        df = pd.read_sql("""
                            select extract(year from completion_date) AS auctionyear,
                            count(*) as listingcount,
                            percentile_cont(0.50) within group (order by price) as price
                            from listings
                            where model_name = '%s' and status = 'Sold' and extract(year from completion_date) > 2015
                            group by model_name, auctionyear
                            order by auctionyear ASC
                        """ % model, session.connection())

        listings_by_year = df['listingcount'].values.astype(int).tolist()
        auctionyear = df['auctionyear'].astype(int).values.tolist() # chart x-axis
        price = df['price'].values.astype(int).tolist() # chart y-axis
        
        # get only the manual transmission listings
        df_manual = pd.read_sql("""
                            select extract(year from completion_date) AS auctionyear,
                            count(*) as listingcount,
                            percentile_cont(0.50) within group (order by price) as price
                            from listings
                            where model_name = '%s' and status = 'Sold' and extract(year from completion_date) > 2015
                            and manual = 'Y'
                            group by model_name, auctionyear
                            order by auctionyear ASC
                        """ % model, session.connection())

        listings_manual = sum(df_manual['listingcount'].values.astype(int).tolist())
        auctionyear_manual = df_manual['auctionyear'].astype(int).values.tolist() # chart x-axis
        price_manual = df_manual['price'].values.astype(int).tolist() # chart y-axis
        
        # get only the low mileage listings
        df_low_mileage = pd.read_sql("""
                            select extract(year from completion_date) AS auctionyear,
                            count(*) as listingcount,
                            percentile_cont(0.50) within group (order by price) as price
                            from listings
                            where model_name = '%s' and status = 'Sold' and extract(year from completion_date) > 2015
                            and mileage < 20000
                            group by model_name, auctionyear
                            order by auctionyear ASC
                        """ % model, session.connection())

        listings_low_mileage = sum(df_low_mileage['listingcount'].values.astype(int).tolist())
        auctionyear_low_mileage = df_low_mileage['auctionyear'].astype(int).values.tolist() # chart x-axis
        price_low_mileage = df_low_mileage['price'].values.astype(int).tolist() # chart y-axis
        
        # to display number of listings per auction year in table
        supporting_data = df.reset_index()[['auctionyear', 'listingcount']].values.astype(int).tolist()
        
        # get additional details and rankings for above table
        df_rankings = pd.read_sql("""
                            SELECT increase, increase_rank
                            FROM rankings
                            WHERE model_name = '%s'
                            """ % model, session.connection())
        
        increase = df_rankings['increase'].item()
        increase_rank = df_rankings['increase_rank'].item()
    
        session.close()
        return render_template('chart.html', make=make, model=model, auctionyear=auctionyear, price=price,
                               supporting_data=supporting_data, dropdown_data=dropdown_data, increase=increase,
                               increase_rank=increase_rank, models_num=models_num, auctionyear_manual=auctionyear_manual,
                               price_manual=price_manual, listings_manual=listings_manual, listings_low_mileage=listings_low_mileage,
                               auctionyear_low_mileage=auctionyear_low_mileage, price_low_mileage=price_low_mileage,
                               listings_by_year=listings_by_year)

def db_connect():
    DATABASE_URI = os.getenv("DATABASE_URI")
    engine = create_engine(DATABASE_URI)
    connection = scoped_session(sessionmaker(bind=engine))
    return connection