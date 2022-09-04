from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from auction.spiders.monthly_scrape import AuctionSpider
import os


# Set the project environment variable (new set of settings), this should be a value in your scrapy.cfg
os.environ['SCRAPY_PROJECT'] = 'auction'

process = CrawlerProcess(get_project_settings())
process.crawl(AuctionSpider)
process.start()