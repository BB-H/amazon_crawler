# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import MySQLdb.cursors
from twisted.enterprise import adbapi

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.utils.project import get_project_settings
import os, logging

SETTINGS = get_project_settings()

class AmazonCnCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item




class MySQLPipeline(object):

	@classmethod
	def from_crawler(cls, crawler):
		return cls(crawler.stats)

	def __init__(self, stats):
		#Instantiate DB
		self.dbpool = adbapi.ConnectionPool('MySQLdb',
			host=SETTINGS['DB_HOST'],
			user=SETTINGS['DB_USER'],
			passwd=SETTINGS['DB_PASSWD'],
			port=SETTINGS['DB_PORT'],
			db=SETTINGS['DB_DB'],
			charset='utf8',
			use_unicode = True,
			cursorclass=MySQLdb.cursors.DictCursor
		)
		self.stats = stats
		dispatcher.connect(self.spider_closed, signals.spider_closed)
	def spider_closed(self, spider):
		""" Cleanup function, called after crawing has finished to close open
			objects.
			Close ConnectionPool. """
		self.dbpool.close()

	def process_item(self, item, spider):
		query = self.dbpool.runInteraction(self.__insert_if_not_exist, item)
		query.addErrback(self._handle_error)
		return item

	def __insert_if_not_exist(self,tx,item):
		sql = "SELECT id from amazon_item where amazon_id = %s"
		res = tx.execute(sql,(item['amazon_id'],))
		if res == 0:
			logging.debug("Insert Amazon item (amazon_id=%s)." %item['amazon_id'])
			#1. Insert item into amamzon_item
			sql = "INSERT INTO \
						amazon_item (name,amazon_id,amazon_category_id,price,additional_charge,oversea_product,third_party,item_link,picture_url) \
						VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
						
			result = tx.execute(sql,(
									item['name'],
									item['amazon_id'],
									item['category_id'],
									item['price'],
									item['additionalCharge'],
									item['overseaProduct'],
									item['thirdParty'],
									item['itemLink'],
									item['pictureURL'],
									)
								)
			#2. Insert category into amazon_category if it's not existed
			categoryInfoList = item['categoryPathInfo']
			catIDs = [catID for (_,catID) in categoryInfoList]
			catIDs = tuple(catIDs)
			sql = "SELECT distinct(amazon_category_id) from amazon_category where amazon_category_id in ("
			for _ in categoryInfoList:
				sql=sql+"%s,"
			sql = sql[0:len(sql)-1]+")"
			tx.execute(sql,catIDs)
			results = tx.fetchall()
			existedCatIDs = [row['amazon_category_id'].encode('utf-8') for row in results]
			
			sql = "insert into amazon_category (name,amazon_category_id,parent_category_id,category_path,category_display_path) values (%s,%s,%s,%s,%s)"
			category_path_nodes = []
			display_path_nodes = []
			parentCategoryID = ""
			for (catName,catID) in categoryInfoList:
				category_path_nodes.append(catID)
				display_path_nodes.append(catName)
				if not existedCatIDs.__contains__(catID):
					tx.execute(sql,(catName,catID,parentCategoryID,",".join(category_path_nodes),">".join(display_path_nodes)))
				parentCategoryID = catID

			self.stats.inc_value('database/items_added')
		else:
			logging.debug("Duplicated item(amazon_id=%s), ignore it!" %item['amazon_id'])
		
	
	def _handle_error(self, e):
		logging.error("DB operating ERROR:%s" %e)  