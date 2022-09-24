import pandas as pd
from flask import Flask, Blueprint, render_template
import psycopg2
from sqlalchemy import create_engine

chart = Blueprint('chart', __name__)

@chart.route('/chart')
def draw_chart():
    
    # DATABASE_URI = 'postgresql+psycopg2://postgres:Porsche911@localhost:5432/postgres'
    # DATABASE_URI = 'postgresql+psycopg2://nmpxbgxicmkrgk:PASSWORD@ec2-44-207-253-50.compute-1.amazonaws.com:5432/dc0erd4bgg1qem' # removed password
    DATABASE_URI = 'postgresql+psycopg2://nmpxbgxicmkrgk:ed76e45376c92c973583cde1eecb086a2f77fcb1a4135415335cc127872251b5@ec2-44-207-253-50.compute-1.amazonaws.com:5432/dc0erd4bgg1qem'
    engine = create_engine(DATABASE_URI)
    dbConnection = engine.connect()
    
    df = pd.read_sql("""
                        select extract(year from completion_date) AS auctionyear,
                        percentile_cont(0.50) within group (order by price) as price
                        from listings
                        where model_name = 'Porsche 911 GT3' and status = 'Sold'
                        group by model_name, auctionyear
                        order by auctionyear ASC
                    """, dbConnection)
    
    # dbConnection.close()

    auctionyear = df['auctionyear'].astype(int).values.tolist() # x-axis
    price = df['price'].values.astype(int).tolist() # y-axis

    return render_template('chart.html', auctionyear=auctionyear, price=price)