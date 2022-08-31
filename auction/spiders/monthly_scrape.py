from urllib import response
from urllib.request import Request
import scrapy
import sqlite3
import time
import datetime
import re as regex
from re import sub
from decimal import Decimal
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from scrapy.crawler import CrawlerProcess


class AuctionSpider(scrapy.Spider):
    name = 'monthlyscrape'
    start_urls = []
    
    def start_requests(self):
        self.connection = sqlite3.connect("auction.db")
        self.c = self.connection.cursor()
        self.c.execute('''
            SELECT url FROM bat_pages WHERE scraped == 0;
            ''')
        for row in self.c.fetchall():
            if row:
                yield scrapy.Request(
                    url=row[0],
                    # meta={'delay_request_by': 2},
                    callback=self.parse
                )
        self.c.close()

    def parse(self, response):

        make = response.xpath("//strong[contains(text(),'Make')]/text()//following::text()[1]").get()
        if response.xpath("//strong[contains(text(),'Model')]/text()//following::text()[1]").get():
            model_name = response.xpath("//strong[contains(text(),'Model')]/text()//following::text()[1]").get()
        else:
            model_name = make
        
        listing_url = response.url
        
        # look for a model year in URL, otherwise skip
        if bool(regex.search(r'\d{4}', listing_url)):
            
            # format data
            model_year = int(regex.search(r'\d{4}', listing_url).group().replace(',',''))
            status = response.xpath("//span[@class='info-value noborder-tiny']/text()").get().split()[0]
            
            # Check to make sure the listing isn't withdrawn
            if status == "Sold" or status == "Bid":
            
                price_temp = response.xpath("//span[@class='info-value noborder-tiny']/strong/text()").get()
                price = int(sub(r'[^\d.]', '', price_temp))
                
                completion_date_temp = response.xpath("//span[@class='info-value noborder-tiny']/span/text()").get().split()[1]
                completion_date = datetime.datetime.strptime(completion_date_temp, '%m/%d/%y').date()
                
                num_comments = int(response.xpath("//span[@class='info-value']/text()").get().replace(',',''))
                
                bids = int(response.xpath("//td[@class='listing-stats-value number-bids-value']/text()").get().replace(',',''))
                
                if response.xpath("//span[@data-stats-item='views']/text()").get():
                    views = int(response.xpath("//span[@data-stats-item='views']/text()").get().split()[0].replace(',',''))
                else:
                    views = 0
                
                if response.xpath("//span[@data-stats-item='watchers']/text()").get():
                    watchers = int(response.xpath("//span[@data-stats-item='watchers']/text()").get().split()[0].replace(',',''))
                else:
                    watchers = 0
                
                details = str([u"".join(li.xpath('.//text()').extract())
                for li in response.xpath("//div[@class='item']/ul/li")])

                # Determine whether a manual transmission
                if regex.sub(r'manual', '', details):
                    manual = 'Y'
                else:
                    manual = 'N'
                
                # Get mileage if available
                listing_detail = ''.join(details).replace('-',' ').replace(u'\\xa0', u' ')
                nums = regex.findall(r'(?:\b\S+\s*){,2}\bMiles', listing_detail, regex.IGNORECASE)
                if nums:
                    try:
                        new_listing_detail = ' '.join(nums)
                        mileage = int(float(new_listing_detail.split()[0].replace(',','').replace('k','000').replace('K','000')))
                    except:
                        mileage = 0
                        pass
                else:
                    mileage = 999999

                yield {
                    'website': "bringatrailer",
                    'listing_url': listing_url,
                    'make': make,
                    'model_name': model_name,
                    'model_year': model_year,
                    'status': status,
                    'price': price,
                    'completion_date': completion_date,
                    'comments': num_comments,
                    'bids': bids,
                    'views': views,
                    'watchers': watchers,
                    'details': details,
                    'manual': manual,
                    'mileage': mileage
                }


process = CrawlerProcess()
process.crawl(AuctionSpider)
process.start()