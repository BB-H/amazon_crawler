# -*- coding: utf-8 -*-
import scrapy
import re,os
import json
import logging
from amazon_cn_crawler.items import AmazonItem
from scrapy.http import Request
from amazon_cn_crawler.HttpProxyFactory import HttpProxyFactory


class AmazonCnSpider(scrapy.Spider):
	'''
	AMAZON CN抓取规则：
	从http://www.amazon.cn/gp/site-directory中抓取所有链接URL，并从URL中抽取关键字‘node’;
	每一个node代表一类商品的ID，该类商品的LIST页为:http://www.amazon.cn/s?node=<NODE ID>;
	从商品LIST页中读取到最大的PAGE数，然后抓取该类商品的每一页：http://www.amazon.cn/s?node=49404071&page=<xx>;
	从商品LIST页中抓取ELEMENT：<li data-asin='xxxx'>,'xxxx'代表了一个商品的ID，然后从商品DETAIL也抓取商品信息：http://www.amazon.cn/dp/<ID>
	'''
	name = "amazon_cn"
	allowed_domains = ["amazon.cn","z.cn","amazon.com","images-amazon.com","amazon-adsystem.com",]
	start_urls = (
		'http://www.amazon.cn/gp/site-directory',
	)
	
	TYPE_LIST_PAGE = "http://www.amazon.cn/s" # "http://www.amazon.cn/s?node=<node id>"
	TYPE_ITEM_PAGE = "http://www.amazon.cn/dp/" # "http://www.amazon.cn/dp/<ID>"


	def __init__(self):
		self.proxyFactory = HttpProxyFactory.getHttpProxyFactory()
		self.pattern_categoryID = re.compile("node=[0-9]+")
		self.pattern_bookWrapper = re.compile("《.+》")
		logging.info("All proxy amount is:%s" %self.proxyFactory.getValidProxyAmount())
		if self.proxyFactory.getValidProxyAmount()>0:
			self.proxyEnbaled = True
			self.proxyinfo = self.proxyFactory.currentProxy
			self.proxyinfo="http://"+self.proxyinfo
			logging.info("[PID:%s] Use Http proxy:%s" %(os.getpid(),self.proxyinfo))
		else:
			self.proxyEnbaled = False
	
	def parse(self, response):
		resp=response
		#allURLs = resp.xpath('//a/@href').extract()
		allURLs = response.xpath('//*[@id="siteDirectory"]/div//a/@href').extract()
		#pattern = re.compile("node=[0-9]+")
		nodeURLs = [url for url in allURLs if url.encode('utf-8').find("node=")>-1]
		for url in nodeURLs:
			match = self.pattern_categoryID.search(url)
			categoryID = match.group().replace('node=','',1)
			if categoryID is None or categoryID.strip()== "":
				continue
			listPageURL = "%s?node=%s" %(self.TYPE_LIST_PAGE,categoryID)
			req = Request(listPageURL,self.parseURL)
			if self.proxyEnbaled:
				req.meta['proxy'] = self.proxyinfo
			yield req
	
	def parseURL(self,response):
		resp = response
		if resp.url.startswith(self.TYPE_LIST_PAGE):
			#1. get all item in this list page
			itemIDs = resp.xpath('//li[@data-asin]').xpath('@data-asin').extract()
			for itemID in itemIDs:
				itemID = itemID.encode("utf-8")
				if itemID is None or itemID.strip() == "":
					continue
				itemPageURL = self.TYPE_ITEM_PAGE+itemID
				req = Request(itemPageURL,self.parseURL)
				if self.proxyEnbaled:
					req.meta['proxiedPhantom']="yes"
				else:
					req.meta['phantom']="yes"
				yield req
			#2. get all list pages in current category if it's in the first page.
			if resp.url.find("page=")<0:
				maxPageNodes = resp.xpath('//*[@id="pagn"]/span[6]/text()')
				if maxPageNodes is not None and len(maxPageNodes)>0:
					maxPage = resp.xpath('//*[@id="pagn"]/span[6]/text()')[0].extract().encode('utf-8')
					for pageNum in range(2,int(maxPage)+1):
						nextPageURL = resp.url+"&page="+str(pageNum)
						req = Request(nextPageURL,self.parseURL)
						if self.proxyEnbaled:
							req.meta['proxy'] = self.proxyinfo
						yield req
		if resp.url.startswith(self.TYPE_ITEM_PAGE):
			name =""
			nameNodes = resp.xpath('//*[@id="productTitle"]/text()') or resp.xpath('//*[@id="btAsinTitle"]/span/text()')
			if nameNodes:
				name = nameNodes[0].extract().encode('utf-8').strip()
			if not name:
				nameNodes = resp.xpath('//*[@id="divsinglecolumnminwidth"]/div[1]/text()')
				if nameNodes:
					name = nameNodes[0].extract().encode('utf-8').strip()
					match = self.pattern_bookWrapper.search(name)
					name = match.group()
			if not name:
				title = resp.xpath('/html/head/title/text()')[0].extract().encode('utf-8').strip()
				match = self.pattern_bookWrapper.search(title)# search 《xxxxx》
				if match:
					name = match.group()
				if not name:
					p = re.compile("-Kindle商店-亚马逊中国|亚马逊中国")
					name = p.sub("",title)

			
			
			amazon_id = resp.url.replace(self.TYPE_ITEM_PAGE,"",1)
			# TODO:price, additionalCharge, overSeaProduct,thirdParty
			price = ""
			#pricePattern = re.compile("\d+\.?\d*")
			pricePattern = re.compile('\d+(,\d\d\d)*.\d+') #example:￥12,500.99
			priceNodes = resp.xpath('//*[@id="priceblock_ourprice"]/text()') 
			if len(priceNodes)<1:
				priceNodes = resp.xpath('//*[@id="priceblock_saleprice"]/text()')
			if len(priceNodes)<1:
				priceNodes = resp.xpath('//*[@id="priceBlock"]/table/tbody/tr/td/b[@class="priceLarge"]/text()')
			if len(priceNodes)<1:
				nodes = resp.xpath('//*[@id and re:test(@id,"a-autoid-\d+-announce")]')
				if len(nodes)>0:
					priceNodes = nodes.xpath('./span[@class="a-color-base"]/span/text()')
			if len(priceNodes)<1:
				priceNodes = resp.xpath('//*[@id="soldByThirdParty"]/span[2]/text()')
			
			if len(priceNodes)>0:
					priceString = priceNodes[0].extract().encode('utf-8')
					m = pricePattern.search(priceString)
					if m is not None:
						price = m.group()
			
			overSeaProduct = "NO"
			overseaNodes = resp.xpath('//*[@id="dynamicDeliveryMessage"]/b/text()')
			if overseaNodes and overseaNodes[0].extract().encode('utf-8').strip()=="美国亚马逊":
				overSeaProduct = "YES"
			overseaNodes = resp.xpath('//*[@id="ddmMerchantMessage"]/b/text()')
			if overseaNodes and overseaNodes[0].extract().encode('utf-8').strip().find("亚马逊海外")>=0:
				overSeaProduct = "YES"
			
			additionalCharge = ""
			shippingAndTaxNodes = response.xpath('//*[@id="ourprice_shippingmessage"]/span/text()') #[0].extract().encode('utf-8')
			if len(shippingAndTaxNodes)>0:
				info = shippingAndTaxNodes[0].extract().encode('utf-8')
				if info.find("运费")>=0 and info.find("关税")>=0:
					m = pricePattern.search(info)
					if m is not None:
						additionalCharge = m.group()
			
			thirdParty = "NO"
			thirdPartyNodes = resp.xpath('//*[@id="ddmMerchantMessage"]/a')
			if len(thirdPartyNodes)>0:
				thirdParty = "YES"


			itemLink = resp.url
			pictureURL = ""
			nodes = response.xpath('//*[@id="landingImage"]/@data-old-hires')
			if len(nodes)>0:
				pictureURL = nodes[0].extract().encode('utf-8')
			if pictureURL == "":
				nodes = response.xpath('//*[@id="imgBlkFront"]/@data-a-dynamic-image')
				if len(nodes)>0:
					j = json.loads(nodes[0].extract().encode('utf-8'))
					if j.keys():
						pictureURL = j.keys()[0].encode('utf-8')
			if pictureURL =="":
				nodes = response.xpath('//*[@id="landingImage"]/@data-a-dynamic-image')
				if len(nodes)>0:
					j = json.loads(nodes[0].extract().encode('utf-8'))
					if j.keys():
						pictureURL = j.keys()[0].encode('utf-8')
			if pictureURL == "":
				nodes = response.xpath('//*[@id="main-image"]/@src')
				if len(nodes)>0:
					pictureURL = nodes[0].extract().encode('utf-8')

			category_id = ""
			#categoryNodes = resp.xpath('//*[@id="wayfinding-breadcrumbs_feature_div"]/ul/li//a')
			categoryLink = resp.xpath('//*[@id="wayfinding-breadcrumbs_feature_div"]/ul/li[last()]//a/@href')[0].extract().encode('utf-8')
			match = self.pattern_categoryID.search(categoryLink)
			category_id = match.group().replace('node=','',1)
			categoryNodes = resp.xpath('//*[@id="wayfinding-breadcrumbs_feature_div"]/ul/li//a')
			
			categoryList = []
			for catNode in categoryNodes:
				catName = catNode.xpath('./text()')[0].extract().encode('utf-8').strip()
				catLink = catNode.xpath('./@href')[0].extract().encode('utf-8')
				match = self.pattern_categoryID.search(catLink)
				catID = match.group().replace('node=','',1)
				categoryList.append((catName,catID))

			item = AmazonItem()
			item.setAttributes(name,amazon_id,category_id,price,additionalCharge,overSeaProduct,thirdParty,itemLink,pictureURL,categoryList)
			logging.debug("Found amazon item:\n%s" %(item.toString()))
			yield item
