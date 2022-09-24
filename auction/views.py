from flask import Blueprint, render_template
import psycopg2


views = Blueprint('views', __name__)

@views.route('/')
def home():
    listing_data = query_auction_db()
    return render_template('home.html', listing_data=listing_data)

def query_auction_db():
    # Connection details
    hostname = 'ec2-44-207-253-50.compute-1.amazonaws.com'
    username = 'nmpxbgxicmkrgk'
    password = 'ed76e45376c92c973583cde1eecb086a2f77fcb1a4135415335cc127872251b5'
    database = 'dc0erd4bgg1qem'
    
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