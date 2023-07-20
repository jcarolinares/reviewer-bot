import sys
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

import logging
from colorlog import ColoredFormatter
import requests
import configparser

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

# scrapy runspider spiders/arduino_docs_bot.py -o results.json -L DEBUG

# TODO Create a report system that keep tracks on an external json file of the boards that already had things like datasheets, making a comparison to raise an alert
# we can already use results.json reading the data and comparing, in case data is not correct, raise an alert.

config_file = "api_credentials.ini"
config = configparser.ConfigParser()
config.read(config_file)

if (config.get("IFTTWebhook", "api_token") == "<IFTTT_WEBHOOK>"):
    print("ERROR-YOU HAVE TO PUT YOUR <IFTTT_WEBHOOK> API TOKEN AT: api_credentials.ini")
    sys.exit()
else:
    ifttt_key = config.get("IFTTWebhook", "api_token")

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
    datasheets_warnings = []

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

            # # FIXME Using this yield is problematic for the CSV export
            # yield {
            #     'family_links': web_item.xpath('a/@href').getall(),
            # }

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

            yield {
                'title': web_item.css('h1.name::text').get(),
                'datasheet': web_item.xpath('//*[@id="overview"]/div/div[1]/div[2]/div[2]/a[2]/@href').get(),
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
                self.datasheets_warnings.append("DATASHEET NOT PRESENT: "+response.url)


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
            log_print("error","DATASHEET NOT WORKING: "+response.url+"\n")
            self.datasheets_errors.append("DATASHEET NOT WORKING: "+response.url)

    def parse_tutorial_page(self, response):
        pass

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
            aux_string = "DATASHEETS TO CHECK: "
            log_print("critical", "DATASHEETS ERRORS OVERVIEW")
            for item in self.datasheets_errors:
                log_print("error",item)
                aux_string = aux_string + item.replace("DATASHEET NOT WORKING:","") + "\n"
            # print(aux_string)
            trigger_ifttt_event("docs_arduino_datasheet_error",ifttt_key,aux_string)
        elif (len(self.datasheets_warnings)!=0):
            aux_string = "DATASHEETS TO CHECK: "
            log_print("warning", "DATASHEETS WARNING OVERVIEW")
            for item in self.datasheets_warnings:
                log_print("warn",item)
                aux_string = aux_string + item.replace("DATASHEET NOT PRESENT: ","") + "\n"
            # print(aux_string)
            # trigger_ifttt_event("docs_arduino_datasheet_error",ifttt_key,aux_string)
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


def trigger_ifttt_event(event_name, key, value):
    url = f'https://maker.ifttt.com/trigger/{event_name}/json/with/key/{key}'
    data = {'value1': value, 'value2': "", 'value3': ""}
    response = requests.post(url, json=data)

    if response.status_code == 200:
        print(f"POST request to IFTTT for event '{event_name}' was successful.")
        # print(f"JSON PAYLOAD {data}")
    else:
        print(f"POST request to IFTTT for event '{event_name}' failed with status code: {response.status_code}")

