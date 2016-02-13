# -*- coding: utf-8 -*-
#!/usr/bin/python
#from scrapy.http import HtmlResponse
#from scrapy.http import Request
import sys, os, logging, traceback
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class PhantomJS(object):

	url = ""
	
	user_agent = (
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"
	)
	
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap["phantomjs.page.settings.userAgent"] = user_agent
	
	def __init__(self):
		self.driver = webdriver.PhantomJS(executable_path = '/usr/local/bin/phantomjs',desired_capabilities=self.dcap,)
		
	def __del__(self):
		self.driver.quit()
	

	def requestByURL(self,url):
		if url is None or url.strip()=="":
			return ""
		try:
			self.driver.get(url)
			content = self.driver.page_source.encode('utf-8')
			return content
		except Exception as e: 
			errorStack = traceback.format_exc()
			print errorStack

			
if __name__ == '__main__':
	#For test purpose
	phantomjs = PhantomJS()
	html1 = phantomjs.requestByURL("http://www.amazon.cn/dp/B00UL50R7U")
	f = file("page.html",'w')
	f.writelines(html1)
	f.close()
	#html2 = phantomjs.requestByURL("http://www.amazon.cn/dp/B00RG87DQ8")
	#f = file("page2.html",'w')
	#f.writelines(html2)
	f.close()