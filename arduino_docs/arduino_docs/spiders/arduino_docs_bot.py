import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class QuotesSpider(CrawlSpider):
    name = "arduino_bot"
    allowed_domains = ['docs.arduino.cc']

    # Not spider variables
    total_products = 0

    def start_requests(self):
        urls = [
            'https://docs.arduino.cc/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_home)
        
    def parse_home(self, response):

        print("HOME PARSER")

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
       
        print("PRODUCT PAGE PARSER")

        self.total_products = self.total_products +1

       # Product page basic info
        for web_item in response.css('div.ProductHeader-module--titleContainer--33ed0'): # It takes the relative links from docs.arduino.org
            yield {
                'title': web_item.css('h1.name::text').get(),
                'description': web_item.xpath('//*[@id="overview"]/div/div[1]/div[2]/div[1]/p/text()').get(), # If the description includes additional tags (See Opta, won't work)
                'product_url': response.url,
                'tutorials': response.xpath('//*[@id="tutorials"]/div/div/div/div/div/a/@href').getall(),
                'url_alive': response.status,
            }
            
            # Warning if a webpage is broken
            if (response.status != 200):
                print("ERROR: WEBPAGE PRODUCT NOT WORKING: "+response.url)
        
        # Final code
        print("Total number of products: "+str(self.total_products))

    def parse_product_page(self, response):
        # TODO the selectors from Scrapy are not enough for scraping a website like this
        # TODO Use beatiful soup as the scrapper
        # TODO Scrape each paragraph and/or section
        pass
