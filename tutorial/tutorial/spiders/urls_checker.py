import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

ext_url_errors=[]

class URLSpider(CrawlSpider):
    name = 'url_spider'
    allowed_domains = ['docs.arduino.cc']  # Replace example.com with the domain you want to crawl
    start_urls = ['https://docs.arduino.cc/tutorials/alvik/getting-started/']  # Replace with the starting URL

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        # Extracting all the URLs from the current page
        urls = response.css('a::attr(href)').extract()

        for url in urls:
            # You can implement any URL checking logic here
            #print("Checking URL:", url)
            if (response.status != 200):
                print("ERROR: "+url)
                ext_url_errors.append(url);

            # You might want to use requests or scrapy.Request to make further requests if needed
            # Example:
            # yield scrapy.Request(url, callback=self.parse_url_content)

    # Example callback to parse the content of the URL
    # def parse_url_content(self, response):
    #     # Parse the content of the URL here
    #     pass


# Running the spider
from scrapy.crawler import CrawlerProcess

process = CrawlerProcess()
process.crawl(URLSpider)
process.start()
print("\n FINAL RESULTS:")
print(ext_url_errors)
