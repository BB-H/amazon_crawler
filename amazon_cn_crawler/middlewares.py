# -*- coding: utf-8 -*-
from scrapy.http import HtmlResponse
from scrapy.http import Request
import os, logging, traceback
from phantomJsTool import PhantomJS as PhantomJSService
from amazon_cn_crawler.HttpProxyFactory import HttpProxyFactory

from scrapy.utils.project import get_project_settings

import MySQLdb

SETTINGS = get_project_settings()

class PhantomJSMiddleware(object):
	phantomJSService = PhantomJSService()

	def __init__(self):
		self.proxyFactory = HttpProxyFactory.getHttpProxyFactory()
	
	# overwrite process request  
	def process_request(self, request, spider):
		if request.meta.has_key('phantom'):# 
			logging.info('[PID:%s] PhantomJS Requesting: %s' %(os.getpid(),request.url))
			#proxyinfo = request.meta['proxy']
			if request.meta['phantom'].strip()=="proxied" and self.proxyFactory.getValidProxyAmount()>0:
				content = self.phantomJSService.requestWithProxy(request.url,self.proxyFactory.getRandomProxy())
			else:
				content = self.phantomJSService.requestByURL(request.url)
			if content is None or content.strip()=="" or content == '<html><head></head><body></body></html>':# 
				logging.debug("[PID:%s] PhantomJS Request failed!" %os.getpid())
				return HtmlResponse(request.url, encoding = 'utf-8', status = 503, body = '')  
			else:
				logging.debug("[PID:%s]PhantomJS Request success!" %os.getpid())
				return HtmlResponse(request.url, encoding = 'utf-8', status = 200, body = content)
 


class ItemFilterMiddleware(object):
	'''
	This is a spider middleware that is used to filter and drop the request which already exists in DB. 
	'''
	TYPE_ITEM_PAGE = "http://www.amazon.cn/dp/" # "http://www.amazon.cn/dp/<ID>"
	
	def __init__(self):
		self.db = MySQLdb.connect(host=SETTINGS['DB_HOST'],
						user=SETTINGS['DB_USER'],
						passwd=SETTINGS['DB_PASSWD'],
						db=SETTINGS['DB_DB'],
						charset = "utf8"
						)
		self.cur = self.db.cursor()
	
	def __del__(self):
		self.db.close()
	
	def process_spider_output(self,response, result, spider):
		for r in result:
			if isinstance(r,Request) and r.url.startswith(self.TYPE_ITEM_PAGE):
				sql = "SELECT id from amazon_item where item_link = %s"
				self.cur.execute(sql, (r.url.strip(),))
				if len(self.cur.fetchall())==0:
					yield r
				else:
					logging.info('The URL exists in DB, skip it: %s' %r.url)
			else:
				yield r
