# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import logging
import sqlite3

class SQLitePipeline(object):
    
    def open_spider(self, spider):
        self.connection = sqlite3.connect("auction.db")
        self.c = self.connection.cursor()
        try:
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS listings(
                    website TEXT,
                    listing_url TEXT,
                    make TEXT,
                    model_name TEXT,
                    model_year INT,
                    status TEXT,
                    price INT,
                    completion_date DATE,
                    comments INT,
                    bids INT,
                    views INT,
                    watchers INT,
                    details TEXT,
                    manual TEXT,
                    mileage INT,
                    UNIQUE (listing_url)
                )
            ''')
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS bat_pages(
                    url TEXT,
                    scraped INT,
                    UNIQUE (url)
                )
            ''')
            self.connection.commit()
        except sqlite3.OperationalError:
            pass
    
    def close_spider(self, spider):
        self.connection.close()
    
    def process_item(self, item, spider):
        self.c.execute('''
            INSERT OR IGNORE INTO listings (website,listing_url,make,model_name,model_year,status,price,completion_date,comments,bids,views,watchers,details,manual,mileage) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            item.get('website'),
            item.get('listing_url'),
            item.get('make'),
            item.get('model_name'),
            item.get('model_year'),
            item.get('status'),
            item.get('price'),
            item.get('completion_date'),
            item.get('comments'),
            item.get('bids'),
            item.get('views'),
            item.get('watchers'),
            item.get('details'),
            item.get('manual'),
            item.get('mileage')
        ))
        self.c.execute('''
            UPDATE bat_pages SET scraped = 1 WHERE url = ?
        ''', (
            item.get('listing_url'),
        ))
        self.connection.commit()
        return item
    
    # def process_item(self, item, spider):
    #     self.c.execute('''
    #         INSERT OR IGNORE INTO bat_pages (url,scraped) VALUES(?,0)
    #     ''', (
    #         item.get('url'),
    #     ))
    #     self.connection.commit()
    #     return item