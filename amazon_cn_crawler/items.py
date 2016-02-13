# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonCnCrawlerItem(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	pass

class AmazonItem(scrapy.Item):
	id = scrapy.Field()
	name = scrapy.Field()
	amazon_id =  scrapy.Field()
	price = scrapy.Field()
	additionalCharge = scrapy.Field()#附加费用(运费，关税等)
	overseaProduct = scrapy.Field()#YES/NO
	thirdParty = scrapy.Field()#YES/NO
	itemLink = scrapy.Field()
	pictureURL = scrapy.Field()
	
	def setAttributes(self,name,amazon_id,price,additionalCharge,overseaProduct,thirdParty,itemLink,pictureURL):
		self['name'] = name
		self['amazon_id'] = amazon_id
		self['price'] = price
		self['additionalCharge'] = additionalCharge
		self['overseaProduct'] = overseaProduct
		self['thirdParty'] = thirdParty
		self['itemLink'] = itemLink
		self['pictureURL'] = pictureURL
	
	
	def __str__(self):
		#return "name=%s,\n amazon_id=%s,\n price=%s,\n additionalCharge=%s,\n overseaProduct = %s,\n thirdParty=%s,\n itemLink=%s,\n pictureURL=%s" %(self.name,self.amazon_id,self.price,self.additionalCharge,self.overseaProduct,self.thirdParty,self.itemLink,self.pictureURL)
		return "name=%s,\n amazon_id=%s,\n price=%s,\n additionalCharge=%s,\n overseaProduct = %s,\n thirdParty=%s,\n itemLink=%s,\n pictureURL=%s" %(self['name'],self['amazon_id'],self['price'],self['additionalCharge'],self['overseaProduct'],self['thirdParty'],self['itemLink'],self['pictureURL'])
	
	def __repr__(self):
		self.__str__()
