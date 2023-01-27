import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

import logging
from colorlog import ColoredFormatter

LOG_LEVEL = logging.DEBUG
LOGFORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"

logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)
log.propagate = False

if (log.hasHandlers()):
    log.handlers.clear()
log.addHandler(stream)

# logging.getLogger().handlers.clear()
# log.debug("A quirky message only developers care about")
# log.addHandler(stream)


# log.info("Curious users might want to know this")
# log.warn("Something is wrong and any user should be informed")
# log.error("Serious stuff, this is red for a reason")
# log.critical("OH NO everything is on fire")

# TODO Scrappy log level control (now debug)


class QuotesSpider(CrawlSpider):
    name = "arduino_bot"
    allowed_domains = ['docs.arduino.cc']

    # Not spider variables
    total_products = 0
    total_datasheets = 0

    def start_requests(self):
        urls = [
            'https://docs.arduino.cc/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_home)
        
    def parse_home(self, response):
        log_print("info","HOME PARSER")

        # Extracting all the links
        for web_item in response.css('div.index-module--product_container--187dc'): # It takes the relative links from docs.arduino.org
            
            # FIXME Using this yield is problematic for the CSV export
            yield {
                'family_links': web_item.xpath('a/@href').getall(),
            }

            # Next group of URLs to go
            next_page = web_item.xpath('a/@href').getall()

            for new_page in next_page:
                if next_page is not None:
                    new_page = response.urljoin(new_page)
                    yield scrapy.Request(new_page, callback=self.parse_product_page)


    def parse_product_page(self, response):
        log_print("info","PRODUCT PAGE PARSER")

        self.total_products = self.total_products +1

       # Product page basic info
        for web_item in response.css('div.ProductHeader-module--titleContainer--33ed0'): # It takes the relative links from docs.arduino.org
            yield {
                'title': web_item.css('h1.name::text').get(),
                'description': web_item.xpath('//*[@id="overview"]/div/div[1]/div[2]/div[1]/p/text()').get(), # If the description includes additional tags (See Opta, won't work)
                'product_url': response.url,
                'tutorials': response.xpath('//*[@id="tutorials"]/div/div/div/div/div/a/@href').getall(),
                'url_alive': response.status,
                'datasheet': web_item.xpath('//*[@id="overview"]/div/div[1]/div[2]/div[2]/a[2]/@href').get(),
            }
            
            # Warning if a webpage is broken
            if (response.status != 200):
                log_print("critical","WEBPAGE PRODUCT NOT WORKING: "+response.url+"\n")

            # Next group of datasheets URLs to go
            next_datasheet = web_item.xpath('//*[@id="overview"]/div/div[1]/div[2]/div[2]/a[2]/@href').get()
            if next_datasheet is not None:
                log_print("info","NEXT DATASHEET "+str(next_datasheet))

                next_datasheet = response.urljoin(next_datasheet)
                yield scrapy.Request(next_datasheet, callback=self.parse_datasheet)
            else:
                log_print("info","DATASHEET NOT PRESENT")


        # Final code
        log_print("info","Total number of products: "+str(self.total_products))
        log_print("info","Total number of datasheets: "+str(self.total_datasheets))


    def parse_product_page_soup(self, response):
        # TODO the selectors from Scrapy are not enough for scraping a website like this
        # TODO Use beatiful soup as the scrapper
        # TODO Scrape each paragraph and/or section
        pass

    def parse_datasheet(self, response):
        log_print("info","DATASHEET PARSER")
        
        self.total_datasheets = self.total_datasheets+1

        # Warning if a datasheet is broken
        if (response.status != 200):
            print("\n*************************************************************************************\n")
            print("\nERROR: DATASHEET PRODUCT NOT WORKING: "+response.url+"\n")
            print("\n*************************************************************************************\n")
        
        # Warning if a webpage is broken
        if (response.status != 200):
            log_print("error","DATASHEET PRODUCT NOT WORKING: "+response.url+"\n")

def log_print(message_level, message):

    if (log.hasHandlers()):
        log.handlers.clear()
        log.addHandler(stream)

    if (message_level == "error"):
        log.error(message)
    elif (message_level == "info"):
        log.info(message)
    elif (message_level == "warn"):
        log.warn(message)
    elif (message_level == "critical"):
        log.critical(message)
