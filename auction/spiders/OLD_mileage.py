import sqlite3
import re

connection = sqlite3.connect("auction.db")
c = connection.cursor()
try:
    c.execute('''
        SELECT listing_url,details FROM listings;
    ''')
except sqlite3.OperationalError:
    pass

for row in c.fetchall():

    listing_url = (str(row[0]))

    # Convert tuple to string
    # listing_detail = ' '.join(filter(lambda x: x if x is not None else '', row[1])).replace('-',' ').replace(u'\\xa0', u' ')
    listing_detail = ''.join(row[1]).replace('-',' ').replace(u'\\xa0', u' ')

    # Find the mileage pattern
    nums = re.findall(r'(?:\b\S+\s*){,2}\bMiles', listing_detail, re.IGNORECASE)

    if nums:
        try:
            new_listing_detail = ' '.join(nums)
            mileage = int(float(new_listing_detail.split()[0].replace(',','').replace('k','000').replace('K','000')))
            try:
                if c.execute('''UPDATE listings SET mileage = ? WHERE listing_url = ?''', (mileage,listing_url)):
                    print("Record updated successfully")
                    connection.commit()
            except sqlite3.OperationalError as error:
                print("Failed to update table", error)
                pass
        except Exception as e:
            pass
    # connection.commit()
c.close()