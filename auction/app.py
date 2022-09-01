from flask import Flask, render_template
import sqlite3


app = Flask(__name__)
db_locale = './auction.db'

@app.route('/')
@app.route('/home')
def home_page():
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

if __name__ == '__main__':
    app.run()
