from flask import Blueprint, render_template
import sqlite3


views = Blueprint('views', __name__)
db_locale = 'auction.db'

@views.route('/')
def home():
    listing_data = query_auction_db()
    return render_template('home.html', listing_data=listing_data)

def query_auction_db():
    connection = sqlite3.connect(db_locale)
    c = connection.cursor()
    try:
        c.execute('''
                  SELECT model_year, model_name, status, price, completion_date FROM listings WHERE make = "Porsche" AND status = "Sold" ORDER BY completion_date DESC
                  ''')
    except sqlite3.OperationalError as error:
        print("Failed to query table", error)
        pass
    listing_data = c.fetchall()
    c.close()
    return listing_data