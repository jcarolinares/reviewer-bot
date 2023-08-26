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


## API Configuration
The scrapper does HTTP calls to different services like **Github** or **IFTTT**. You will need personal API tokens from both sites.

Put your personal API tokens inside the file `api_credentials.ini`

```
[IFTTWebhook]
api_token: <THINGIVERSE_API_TOKEN>

[GithubAPI]
api_token: <GITHUB_TOKEN>
```

Replace <name_items> with your tokens, no quotes are needed.

**Remember to never share or upload your API TOKENS**

## How to run the Spider

Go inside /reviewer-bot/arduino_docs/arduino_docs and:

``` bash
scrapy runspider spiders/arduino_docs_bot.py -o test.json
```

