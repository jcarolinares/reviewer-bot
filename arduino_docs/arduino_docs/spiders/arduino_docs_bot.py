import scrapy


class QuotesSpider(scrapy.Spider):
    name = "arduino_bot"

    def start_requests(self):
        urls = [
            'https://docs.arduino.cc/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_home)

    def parse_home(self, response):

        print("TEST PARSE")

        # # Data to extract
        # for web_item in response.css('div.index-module--main_wrapper--7d946'):
        #     yield {
        #         'category': web_item.css('h3::text').getall(),
        #         'list_of_products': web_item.css('div.index-module--product_container--187dc').getall(),
        #         'link': web_item.xpath('a/@href').extract(),
        #     }

        # Extracting all the links
        for web_item in response.css('div.index-module--product_container--187dc'): # It takes the relative links from docs.arduino.org
            yield {
                'link': web_item.xpath('a/@href').getall(),
            }

        # Next url to go
        next_page = web_item.xpath('a/@href').getall()

        for new_page in next_page:
            if next_page is not None:
                print("JULIAN")
                new_page = response.urljoin(new_page)
                yield scrapy.Request(new_page, callback=self.parse_product_page)

        # # Next url to go
        # next_page = response.css('li.next a::attr(href)').get()
        # if next_page is not None:
        #     next_page = response.urljoin(next_page)
        #     yield scrapy.Request(next_page, callback=self.parse)

        # # Next url to go
        # next_page = response.xpath('a/@href').getall()
        # if next_page is not None:
        #     print("NEXT PAGE")
        #     print(next_page)
        #     yield response.follow(next_page, callback=self.parse)


    def parse_product_page(self, response):
       
        print("PRODUCT PAGE")

       # Links to tutorials
        for web_item in response.css('div.ProductHeader-module--titleContainer--33ed0'): # It takes the relative links from docs.arduino.org
            yield {
                'title': web_item.css('h1.name::text').getall(),
                'description': web_item.css('div.ProductHeader-module--description--4c8f4.ProductHeader-module--content--319f1.p::text').getall(),
            }
