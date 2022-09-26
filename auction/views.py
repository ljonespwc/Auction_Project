import pandas as pd
import psycopg2
import os
from flask import Flask, Blueprint, render_template
from sqlalchemy import create_engine


views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')

@views.route('/chart')
def draw_chart():
    dbConnection = db_connect()
    df = pd.read_sql("""
                        select extract(year from completion_date) AS auctionyear,
                        percentile_cont(0.50) within group (order by price) as price
                        from listings
                        where make = 'Porsche' and status = 'Sold'
                        group by make, auctionyear
                        order by auctionyear ASC
                    """, dbConnection)

    auctionyear = df['auctionyear'].astype(int).values.tolist() # x-axis
    price = df['price'].values.astype(int).tolist() # y-axis

    dbConnection.close()
    return render_template('chart.html', auctionyear=auctionyear, price=price)

def db_connect():
    DATABASE_URI = os.getenv("DATABASE_URI")
    engine = create_engine(DATABASE_URI)
    connection = engine.connect()
    return connection