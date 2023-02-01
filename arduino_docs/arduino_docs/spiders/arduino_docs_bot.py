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


# scrapy runspider spiders/arduino_docs_bot.py -o results.json -L DEBUG

class QuotesSpider(CrawlSpider):

    # Spider variables
    name = "arduino_bot"
    allowed_domains = ['docs.arduino.cc']
    handle_httpstatus_list = [404] # To handle 404 requests

    # Not spider variables
    total_products = 0
    total_datasheets = 0
    product_pages_errors = []
    datasheets_errors = []

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
                    new_page = response.urljoin(new_page)  #+"2" # used to corrupt urls to test 404
                    log_print("info","New page: "+new_page)
                    yield scrapy.Request(new_page, callback=self.parse_product_page)


    def parse_product_page(self, response):
        print("\n")
        log_print("info","PRODUCT PAGE PARSER")

        # Warning if a webpage is broken
        if (response.status != 200):
            log_print("critical","WEBPAGE PRODUCT NOT WORKING: "+response.url+"\n")
            self.product_pages_errors.append("WEBPAGE PRODUCT NOT WORKING: "+response.url)

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
                'full-pinout': web_item.xpath('//*[@id="resources"]/div/div/div[3]/div[2]/div/a/@href').getall(), # FIXME not differences between pdfs, eagle files... use beatifulsoup
                'troubleshooting': web_item.xpath('//*[@id="troubleshooting"]/div/div/div/div/a/@href').getall(),
            }

            # log_print("info", "debug ")
            # log_print("info",web_item.xpath('//*[@id="troubleshooting"]/div/div/div/div/a/@href').getall())

            # TODO call here parse_product_page_soup() function to extract and add more information

            # Next group of datasheets URLs to go
            next_datasheet = web_item.xpath('//*[@id="overview"]/div/div[1]/div[2]/div[2]/a[2]/@href').get()
            if next_datasheet is not None:
                log_print("info","NEXT DATASHEET "+str(next_datasheet))

                next_datasheet = response.urljoin(next_datasheet) #+"2" # 2 to test 404 
                log_print("info",next_datasheet)
                yield scrapy.Request(next_datasheet, callback=self.parse_datasheet)
            else:
                log_print("warn","DATASHEET NOT PRESENT")


        #//*[@id="troubleshooting"]/div/div/div[2]/div[1]/a

        # # Final report
        # print("\n")
        # log_print("info","FINAL REPORT")
        # log_print("info","Total number of products: "+str(self.total_products))
        # log_print("info","Total number of datasheets: "+str(self.total_datasheets))

        # # Product pages overview report
        # print("\n")
        # if (len(self.product_pages_errors)!=0):
        #     log_print("critical", "PRODUCT PAGES ERRORS OVERVIEW")
        #     for item in self.product_pages_errors:
        #         log_print("error",item)
        # else:
        #     log_print("info", "NO PRODUCT PAGES ERRORS FOUND")

        # # Datasheets overview report
        # print("\n")
        # if (len(self.datasheets_errors)!=0):
        #     log_print("critical", "DATASHEETS ERRORS OVERVIEW")
        #     for item in self.datasheets_errors:
        #         log_print("error",item)
        # else:
        #     log_print("info", "NO DATASHEET ERRORS FOUND")


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
            log_print("error","DATASHEET PRODUCT NOT WORKING: "+response.url+"\n")
            self.datasheets_errors.append("DATASHEET PRODUCT NOT WORKING: "+response.url)

    def closed(self, reason):
        # Final report
        print("\n")
        log_print("info","FINAL REPORT")
        log_print("info","Total number of products: "+str(self.total_products))
        log_print("info","Total number of datasheets: "+str(self.total_datasheets))

        # Product pages overview report
        print("\n")
        if (len(self.product_pages_errors)!=0):
            log_print("critical", "PRODUCT PAGES ERRORS OVERVIEW")
            for item in self.product_pages_errors:
                log_print("error",item)
        else:
            log_print("info", "NO PRODUCT PAGES ERRORS FOUND")

        # Datasheets overview report
        print("\n")
        if (len(self.datasheets_errors)!=0):
            log_print("critical", "DATASHEETS ERRORS OVERVIEW")
            for item in self.datasheets_errors:
                log_print("error",item)
        else:
            log_print("info", "NO DATASHEET ERRORS FOUND")


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

