from flask import Blueprint, render_template
import psycopg2


views = Blueprint('views', __name__)

@views.route('/')
def home():
    listing_data = query_auction_db()
    return render_template('home.html', listing_data=listing_data)

def query_auction_db():
    # Connection details
    hostname = 'ec2-44-207-126-176.compute-1.amazonaws.com'
    username = 'anoedcsrcyzdwc'
    password = '73428c28718f0b02a4d004d3e535d5ed9b9309e80d9cf5f5b5790830ced3e308'
    database = 'dc0snn24f0j4l0'
    
    connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    c = connection.cursor()
    try:
        c.execute('''
                  SELECT model_year, model_name, status, price, completion_date FROM listings WHERE make = 'Porsche' AND status = 'Sold' ORDER BY completion_date DESC
                  ''')
    except psycopg2.OperationalError as error:
        print("Failed to query table", error)
        pass
    listing_data = c.fetchall()
    c.close()
    return listing_data