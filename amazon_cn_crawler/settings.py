# -*- coding: utf-8 -*-

# Scrapy settings for amazon_cn_crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

import logging
from logging.handlers import RotatingFileHandler
from scrapy.utils.log import configure_logging


BOT_NAME = 'amazon_cn_crawler'

SPIDER_MODULES = ['amazon_cn_crawler.spiders']
NEWSPIDER_MODULE = 'amazon_cn_crawler.spiders'


###### DB config ######
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'xxx'
DB_PASSWD = 'xxxx'
DB_DB = 'xxxx'



# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36'

#USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
#USER_AGENT = "Mozilla/4.0 (compatible; MSIE 6.0; America Online Browser 1.1; Windows NT 5.1; SV1; .NET CLR 1.0.3705; .NET CLR 1.1.4322; Media Center PC 3.1)"
#USER_AGENT = "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.4 (Change: )"
#USER_AGENT = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)"
#USER_AGENT = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en; rv:1.8.1.6) Gecko/20070809 Camino/1.5.1"
#USER_AGENT = "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13 "
#USER_AGENT = "Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10"

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   	#'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
   	#'Accept-Language': 'en',
   	'Accept-Encoding':'gzip, deflate, sdch',
	'Accept-Language':'en-US,en;q=0.8,fr;q=0.6,ja;q=0.4,zh-CN;q=0.2,zh-TW;q=0.2',
	'Cache-Control':'max-age=0',
	'Connection':'keep-alive',
	'Host':'www.amazon.cn',
	'Upgrade-Insecure-Requests':'1',
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'amazon_cn_crawler.middlewares.ItemFilterMiddleware': 543,
}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
#    'mybid.middlewares.MyCustomDownloaderMiddleware': 543,
     'amazon_cn_crawler.middlewares.PhantomJSMiddleware':520,
     #'amazon_cn_crawler.middlewares.RandomUserAgentMiddleware': 400, # enable random user-agent, all user agents define in 'USER_AGENT_LIST'
}

#USER_AGENT_LIST = "./amazon_cn_crawler/useragents.txt"

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'amazon_cn_crawler.pipelines.MySQLPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'

'''
configure_logging(install_root_handler=False)
logging.basicConfig(
    filename='z.log',
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)
'''
log_name = 'z.log'
logging.basicConfig(filename=log_name)
log = logging.getLogger()
handler = RotatingFileHandler(log_name,maxBytes=20*1024*1024,backupCount=5)
log.addHandler(handler)
