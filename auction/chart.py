import pandas as pd
import psycopg2
import os
from flask import Flask, Blueprint, render_template
from sqlalchemy import create_engine

chart = Blueprint('chart', __name__)

@chart.route('/chart')
def draw_chart():
    
    DATABASE_URI = os.getenv("DATABASE_URI")
    
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