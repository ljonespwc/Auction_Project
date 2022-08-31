import scrapy
import datetime
import re as regex
from re import sub
from scrapy.crawler import CrawlerProcess


class SinglePageSpider(scrapy.Spider):
    name = 'single'
    start_urls = []
    
    def start_requests(self):
        yield scrapy.Request(
            url='https://bringatrailer.com/listing/1929-packard-640-custom-eight-club-sedan/',
            meta={'delay_request_by': 2},
            callback=self.parse)

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

                print("make: " + str(make))
                print("model_name: " + str(model_name))
                print("model_year: " + str(model_year))
                print("status: " + str(status))
                print("price: " + str(price))
                print("completion_date: " + str(completion_date))
                print("comments: " + str(num_comments))
                print("bids: " + str(bids))
                print("views: " + str(views))
                print("watchers: " + str(watchers))
                print("details: " + details)
                print("manual: " + manual)
                print("mileage: " + str(mileage))


process = CrawlerProcess()
process.crawl(SinglePageSpider)
process.start()