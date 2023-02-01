# Reviewer-bot
A bot crawler to review broken links or others errors on docs.arduino.com

## Dependencies

This programs runs under Python 3

### Scrapy
``` bash
pip install scrapy
```

or

``` bash
sudo apt install python3-scrapy
```

### ColorLog
``` bash
pip install colorlog
```

or

``` bash
sudo apt install python3-colorlog
```

## How to run the Spider

Go inside /reviewer-bot/arduino_docs/arduino_docs and:

``` bash
scrapy runspider spiders/arduino_docs_bot.py -o test.json
```

