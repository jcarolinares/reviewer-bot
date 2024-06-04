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

if (config.get("GithubAPI", "api_token") == "<GITHUB_TOKEN>"):
    print("ERROR-YOU HAVE TO PUT YOUR <GITHUB_TOKEN> API TOKEN AT: api_credentials.ini")
    sys.exit()
else:
    github_key = config.get("GithubAPI", "api_token")





class QuotesSpider(CrawlSpider):

    # Spider variables
    name = "arduino_bot"
    allowed_domains = ['docs.arduino.cc']
    handle_httpstatus_list = [404] # To handle 404 requests
    number_categories = 10

    # Not spider variables
    total_products = 0
    total_datasheets = 0
    total_tutorials = 0
    product_pages_errors = []
    datasheets_errors = []
    datasheets_warnings = []
    tutorial_ext_urls_errors = []

    ignore_url_list = ["https://unicode.org/emoji/charts/full-emoji-list.html"]

    def start_requests(self):
        urls = [
            'https://docs.arduino.cc/hardware/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_home)

    def parse_home(self, response):
        log_print("info","HOME PARSER")

        # FIXME None of these methods are worth with the actual webpage being dynamic, the effort in development will be big and in maintenance too. 
        # TODO It is better to be practical so create a manual list of products with the permalinks

        # sidebar_info = response.css('div.sidebar > div.sidebar__first-level')
        # log_print("info", str(sidebar_info))

        # page_urls = sidebar_info.css('a::attr(href)').getall() # This onlt gets the "visible ones"


        # # page_urls = response.css('a::attr(href)').getall() # This onlt gets the "visible ones"
        # for url in page_urls:
        #     log_print("info", str(url))
        
        # #layout > main > div.sidebar > div.sidebar__first-level


        # Extracting all the links
        # Selector #layout > main > div.sidebar > div.sidebar__first-level > div > button.sidebar__categories.accordion > div.sidebar__main-category.sidebar__main-category--opened > div.sidebar__container > h5
        #layout > main > div.sidebar > div.sidebar__first-level > div > button:nth-child(1) > div > div.sidebar__container > h5
        #layout > main > div.sidebar > div.sidebar__first-level > div > button:nth-child(2) > div > div.sidebar__container > h5
        # debug_string = response.css('div.sidebar > div.sidebar__first-level > div > button:nth-child(1) > div > div.sidebar__container > h5::text').get()
        # log_print("error", str(debug_string))
        #layout > main > div.sidebar > div.sidebar__first-level > div > button:nth-child(1) > div > div.sidebar__container > h5


        # Parsing the navigation bar categories to get each product link
        # for i in range(self.number_categories):
        #     log_print("error", str(i))            
        #     # web_item = response.css(f'div.sidebar > div.sidebar__first-level > div > button:nth-child({i}) > div > div.sidebar__container > h5')
        #     web_item = response.css(f'div.sidebar > div.sidebar__first-level > div.sidebar__navigation >  button:nth-child(1) > div:nth-child(2) > div.sidebar__links') # Should work but is not
        #     log_print("error", (web_item))
            # links_containers = web_item.xpath('/div[2]/div[2]').getall()
            # log_print("error", str(links_containers))
            # <div class="sidebar__main-category sidebar__main-category--opened"><div class="sidebar__container"><h5>MKR Family</h5></div><div class="sidebar__main-category--icon"><svg width="10" height="6" viewBox="0 0 10 6" fill="none" xmlns="http://www.w3.org/2000/svg" style="transform:rotate(270deg)"><g id="Icon"><path id="Vector" d="M5.00012 5.12463C4.91786 5.1251 4.83632 5.10934 4.76017 5.07824C4.68403 5.04713 4.61477 5.0013 4.55637 4.94338L0.806366 1.19338C0.688676 1.07569 0.622559 0.916066 0.622559 0.749627C0.622559 0.583189 0.688676 0.423567 0.806366 0.305877C0.924055 0.188188 1.08368 0.12207 1.25012 0.12207C1.41655 0.12207 1.57618 0.188188 1.69387 0.305877L5.00012 3.61838L8.30637 0.305877C8.42406 0.188188 8.58368 0.12207 8.75012 0.12207C8.91656 0.12207 9.07618 0.188188 9.19387 0.305877C9.31156 0.423567 9.37767 0.583189 9.37767 0.749627C9.37767 0.916066 9.31156 1.07569 9.19387 1.19338L5.44387 4.94338C5.38547 5.0013 5.31621 5.04713 5.24006 5.07824C5.16391 5.10934 5.08237 5.1251 5.00012 5.12463Z" fill="#7F8C8D"></path></g></svg></div></div>

        #     # next_page = web_item.xpath('a/@href').getall()
        #     # log_print("error", str(next_page))
        #layout > main > div.sidebar > div.sidebar__first-level > div > button:nth-child(1) > div:nth-child(2) > div.sidebar__links

        #layout > main > div.sidebar > div.sidebar__first-level > div > button:nth-child(1) > div:nth-child(2)



        #layout > main > div.sidebar > div.sidebar__first-level > div > button.sidebar__categories.accordion > div.sidebar__main-category.sidebar__main-category--opened > div.sidebar__container > h5
        #layout > main > div.sidebar > div.sidebar__first-level > div > button:nth-child(1) > div.sidebar__main-category.sidebar__main-category--opened > div.sidebar__container > h5
        #layout > main > div.sidebar > div.sidebar__first-level > div > button:nth-child(1) > div:nth-child(2) > div.sidebar__links
        #layout > main > div.sidebar > div.sidebar__first-level > div > button:nth-child(1) > div:nth-child(2) > div.sidebar__links
        #layout > main > div.sidebar > div.sidebar__first-level > div > button:nth-child(1) > div:nth-child(2)
        #layout > main > div.sidebar > div.sidebar__first-level > div > button:nth-child(1) > div.sidebar__main-category.sidebar__main-category--opened
       #layout > main > div.sidebar > div.sidebar__first-level > div > button:nth-child(1) > div:nth-child(2)
        # for web_item in response.css(f'div.sidebar > div.sidebar__first-level > div > button:nth-child({number_categories-1}) > div > div.sidebar__container > h5'):
        #     log_print("error", str(web_item))

        # for web_item in response.css('div.sidebar > div.sidebar__first-level > div > button.sidebar__categories.accordion > div.sidebar__main-category.sidebar__main-category--opened > div.sidebar__container > h5::text').get(): # It takes the relative links from docs.arduino.org
        #     # # FIXME Using this yield is problematic for the CSV export
        #     # yield {
        #     #     'family_links': web_item.xpath('a/@href').getall(),
        #     # }
        #     log_print("info", "HARDWARE containers debug: "+str(web_item))

        #     # Next group of URLs to go
        #     next_page = web_item.xpath('a/@href').getall()

        #     for new_page in next_page:
        #         if next_page is not None:
        #             new_page = response.urljoin(new_page)  #+"2" # used to corrupt urls to test 404
        #             log_print("info","New page: "+new_page)
        #             yield scrapy.Request(new_page, callback=self.parse_product_page)

    def parse_product_page(self, response):
        print("\n")
        log_print("info", f"PRODUCT PAGE PARSER: {response.url}")

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
                'datasheet': web_item.xpath('//*[@id="overview"]/div/div[1]/div[2]/div[2]/a[contains(text(), "DATASHEET")]/@href').get(),
                'full-pinout': web_item.xpath('//*[@id="resources"]/div/div/div[3]/div[2]/div/a/@href').getall(), # FIXME not differences between pdfs, eagle files... use beatifulsoup
                'troubleshooting': web_item.xpath('//*[@id="troubleshooting"]/div/div/div/div/a/@href').getall(),
            }
            # FIXME Portenta Machine Control datasheet xpath: "//*[@id="overview"]/div/div[1]/div[2]/div[2]/a" FIXED WITH '//*[@id="overview"]/div/div[1]/div[2]/div[2]/a[contains(text(), "DATASHEET")]/@href'
            # //a[contains(text(), 'programming')]/@href

            # Datasheet link

            # TODO call here parse_product_page_soup() function to extract and add more information

            # Datasheets scrapping
            next_datasheet = web_item.xpath('//*[@id="overview"]/div/div[1]/div[2]/div[2]/a[contains(text(), "DATASHEET")]/@href').get()
            if next_datasheet is not None:
                log_print("info","NEXT DATASHEET "+str(next_datasheet))

                next_datasheet = response.urljoin(next_datasheet) #+"2" # 2 to test 404 
                log_print("info",next_datasheet)
                yield scrapy.Request(next_datasheet, callback=self.parse_datasheet)
            else:
                log_print("warn","DATASHEET NOT PRESENT")
                self.datasheets_warnings.append("DATASHEET NOT PRESENT: "+response.url)

            # Tutorial Scrapping
            tutorials_list = response.xpath('//*[@id="tutorials"]/div/div/div/div/div/a/@href').getall()

            # Tutorials list print
            # log_print("warn", f"TUTORIALS LIST: {tutorials_list}")
            log_print("info", "\n\nTUTORIALS LIST:")
            for tutorial in tutorials_list:
                log_print("info", tutorial)
            log_print("info", "\n\n")

            for next_tutorial in tutorials_list:
                if next_tutorial is not None:
                    log_print("info","NEXT TUTORIAL "+str(next_tutorial))

                    next_tutorial = response.urljoin(next_tutorial) #+"2" # 2 to test 404 
                    log_print("info",next_tutorial)
                    yield scrapy.Request(next_tutorial, callback=self.parse_tutorial_page)
                else:
                    log_print("warn","TUTORIAL NOT PRESENT")
                    self.datasheets_warnings.append("TUTORIAL NOT PRESENT: "+response.url)



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

    def parse_tutorial_page(self, response): # TODO Use beatiful soup, almost impossible with scrappy
        log_print("info", f"TUTORIAL PARSER: {response.url}")

        self.total_tutorials = self.total_tutorials+1

        # Warning if a tutorial is broken
        if (response.status != 200):
            log_print("error","TUTORIAL NOT WORKING: "+response.url+"\n")
            # self.datasheets_errors.append("DATASHEET NOT WORKING: "+response.url)

       # Product page basic info
        for web_item_tutorial in response.css('div.tutorial-module--left--f2811'): # It takes the relative links from docs.arduino.org
            # print(response.css('div.tutorial-module--left--f2811'))
            # print(response.xpath('//*[@id="layout"]/div/div[1]').get())
            # print(response.css('h5::text').getall())
            yield {
                'title': web_item_tutorial.css('h1::text').get(),
                'tutorial_url': response.url,
                'description': web_item_tutorial.xpath('//h1/following-sibling::div[1]/text()').get(),
                'author': web_item_tutorial.css('div.tutorial-module--metadata--b16ef.tutorial-module--author--c9a7a::text').get(), # FIXME Not working
                'sections': web_item_tutorial.css('h2::text').getall(),
                'url_alive': response.status,
                'urls': web_item_tutorial.css('a::attr(href)').extract(), #.getall()
                # 'description': response.xpath('//*[@id="layout"]/div/div[1]/div/ul/li[1]/div/text()').get(), # If the description includes additional tags (See Opta, won't work)
                # 'product_url': response.url,
                # 'tutorials': web_item_tutorial.xpath('//*[@id="tutorials"]/div/div/div/div/div/a/@href').getall(),
                # 'url_alive': web_item_tutorial.status,
                # 'datasheet': web_item_tutorial.xpath('//*[@id="overview"]/div/div[1]/div[2]/div[2]/a[contains(text(), "DATASHEET")]/@href').get(),
                # 'full-pinout': web_item_tutorial.xpath('//*[@id="resources"]/div/div/div[3]/div[2]/div/a/@href').getall(), # FIXME not differences between pdfs, eagle files... use beatifulsoup
                # 'troubleshooting': web_item_tutorial.xpath('//*[@id="troubleshooting"]/div/div/div/div/a/@href').getall(),
            }

            # URLs to file
            tutorial_urls = web_item_tutorial.css('a::attr(href)').extract()

            # Use a set to eliminate duplicates
            unique_urls = list(set(tutorial_urls))

            f_404 = open("404_tutorials_ext_urls.txt", mode='a')
            f_404.close()

            s = requests.Session()  # It creates a session to speed up the downloads

            with open("tutorials_ext_urls.txt", mode='a') as f:
                for url in unique_urls:
                    if "/static/" in url: # To avoid adding static resources like images
                        log_print("info", f"Static resource ignored: {url}")
                        continue
                    elif line_exists("tutorials_ext_urls.txt", url): # To avoid checking duplicates
                        log_print("info", f"Link duplicated - Ignoring: {url}")
                        if line_exists("404_tutorials_ext_urls.txt", url):
                            log_print("error", f"URL BROKEN ALREADY CHECKED -> Tutorial: {response.url} Link: {url}")
                            self.tutorial_ext_urls_errors.append(f"Tutorial: {response.url} Link: {url}")
                        continue
                    else:
                        new_link = ""
                        new_link = response.urljoin(url)
                        f.write(new_link+"\n")

                        # Check if the links is alive
                        for ignore_url in self.ignore_url_list:
                            if url == ignore_url:
                                log_print("warn", f"Ignoring URL: {url}")
                                break
                            else:
                                if "http" in url:
                                    try:
                                        log_print("info", f"Checking: {url}")
                                        r = s.get(url, timeout = (10, 30)) # Check the link
                                        if r.status_code!=200:
                                            log_print("error", f"URL BROKEN -> Tutorial: {response.url} Link: {url} Status: {r.status_code}")
                                            self.tutorial_ext_urls_errors.append(f"Tutorial: {response.url} Link: {url} Status: {r.status_code}")
                                            with open("404_tutorials_ext_urls.txt", mode='a') as f_404:
                                                f_404.write(url+"\n")
                                                f_404.close()
                                    except requests.exceptions.ConnectionError:
                                        log_print("error",'Network connection error')
                                        log_print("error", f"URL BROKEN -> Tutorial: {response.url} Link: {url} Status: {r.status_code}")
                                        self.tutorial_ext_urls_errors.append(f"Tutorial: {response.url} Link: {url} Status: {r.status_code}")
                                        with open("404_tutorials_ext_urls.txt", mode='a') as f_404:
                                            f_404.write(url+"\n")
                                            f_404.close()
                                    except requests.exceptions.Timeout:
                                        log_print("error",'The request timed out')
                                        log_print("error", f"URL BROKEN -> Tutorial: {response.url} Link: {url} Status: {r.status_code}")
                                        self.tutorial_ext_urls_errors.append(f"Tutorial: {response.url} Link: {url} Status: {r.status_code}")
                                        with open("404_tutorials_ext_urls.txt", mode='a') as f_404:
                                            f_404.write(url+"\n")
                                            f_404.close()
            f.close()


    def closed(self, reason):
        # Final report
        print("\n")
        log_print("info","FINAL REPORT")
        log_print("info","Total number of products: "+str(self.total_products))
        log_print("info","Total number of tutorials: "+str(self.total_tutorials))
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
            log_print("info","RENDER DATASHEETS ON DOCS ARDUINO TO SOLVE ISSUES")
            trigger_render_datasheet_action(github_key)
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

        # Tutorials external url references overview report
        print("\n")
        if (len(self.tutorial_ext_urls_errors)!=0):
            aux_string = "TUTORIAL EXT URLS TO CHECK: "
            log_print("critical", "TUTORIAL EXT URLS ERRORS OVERVIEW")
            for item in self.tutorial_ext_urls_errors:
                log_print("error",item)

            with open("tutorial_broken_ext_links.txt", 'w') as output_file:
                for line in self.tutorial_ext_urls_errors:
                    output_file.write(line+"\n")
                output_file.close()
            # trigger_ifttt_event("docs_arduino_datasheet_error",ifttt_key,aux_string)
            # log_print("info","RENDER DATASHEETS ON DOCS ARDUINO TO SOLVE ISSUES")
            # trigger_render_datasheet_action(github_key)
        else:
            log_print("info", "NO TUTORIALS EXT URLS ERRORS FOUND")


            # # External Tutorial URLs file cleaning with no duplicates
            # # Input file with duplicate lines
            # input_file_path = "tutorials_ext_urls.txt"

            # # Output file to store unique lines
            # output_file_path = "tutorials_ext_urls.txt"

            # # Read lines from the input file
            # with open(input_file_path, 'r') as input_file:
            #     lines = input_file.readlines()

            # # Use a set to eliminate duplicate lines
            # unique_lines = set(lines)

            # # Write the unique lines to the output file
            # with open(output_file_path, 'w') as output_file:
            #     output_file.writelines(unique_lines)




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

def trigger_render_datasheet_action(github_token):
    url = f'https://api.github.com/repos/arduino/docs-content/actions/workflows/render-datasheets.yaml/dispatches'
    data = {"ref": "main"}
    headers = {"Authorization": f"Bearer {github_token}", "Accept": "application/vnd.github.v3+json"}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200 or response.status_code == 204 :
        print(f"POST to trigger Render Datasheet Action was succesful")
        # print(f"JSON PAYLOAD {data}")
    else:
        print(f"POST to trigger Render Datasheet Action failed with status code: {response.status_code}")


def line_exists(file_path, target_line):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip() == target_line.strip():
                    return True  # The line already exists in the file
        return False  # The line does not exist in the file
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return False
