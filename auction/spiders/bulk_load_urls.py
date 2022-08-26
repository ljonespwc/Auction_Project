import scrapy
from selenium import webdriver
from scrapy.selector import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import selenium
# import time
# import datetime
# import re as regex
# from re import sub
# from decimal import Decimal
# from scrapy.shell import inspect_response
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains


class URLSpider(scrapy.Spider):
    name = 'bulkurls'
    custom_settings = {'DOWNLOAD_DELAY': .05}
    start_urls = ('https://bringatrailer.com/models/',)

    def parse(self, response):
        options = webdriver.FirefoxOptions()
        # options.add_argument("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15")
        options.add_argument("--disable-notifications")
        options.add_argument("--incognito")
        options.add_argument("--disable-extensions")
        options.add_argument("-–disable-web-security")
        options.add_argument("--no-sandbox") 	
        options.add_argument("--headless")
        
        self.driver = webdriver.Firefox(executable_path='/Users/lancejones/Library/Application Support/WebDriverManager/gecko/v0.29.0/geckodriver-v0.29.0-macos/geckodriver', options=options)
        self.driver.get("https://bringatrailer.com/models/")
        
        # get page source for all models page
        models_html = self.driver.page_source
        response_models = Selector(text=models_html)
        models = response_models.xpath("//a[@class='previous-listing-image-link']")
        
        # loop through and load each model page
        for model in models:
            model_url = model.xpath(".//@href").get()
            self.driver.get(model_url)
            
            # load all listings on a model page
            while True:
                try:
                    WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button']/span[@data-bind='hidden: working']"))).click()
                except Exception as e:
                    break
            
            # get page source for all model listings
            model_listings_html = self.driver.page_source
            response_listings = Selector(text=model_listings_html)
            
            # loop through and load each listing page
            listings = response_listings.xpath("//div[@class='overlayable']/div[@class='blocks']/div/a")
            for listing in listings:
                listing_url = listing.xpath(".//@href").get()

                yield {
                    'url': listing_url
                }

        self.driver.close()