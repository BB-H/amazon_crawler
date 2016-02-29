# -*- coding: utf-8 -*-
#!/usr/bin/python
#from scrapy.http import HtmlResponse
#from scrapy.http import Request
import sys, os, logging, traceback, random
from urllib2 import URLError
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class PhantomJS(object):
	

	user_agents = [
				("Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"),
				("Mozilla/4.0 (compatible; MSIE 6.0; America Online Browser 1.1; Windows NT 5.1; SV1; .NET CLR 1.0.3705; .NET CLR 1.1.4322; Media Center PC 3.1)"),
				("Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.4 (Change: )"),
				("Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13"),
				("Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10"),
	]
	
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	#dcap["phantomjs.page.settings.userAgent"] = user_agent
	dcap["phantomjs.page.settings.userAgent"] = random.choice(user_agents)
	
	def __init__(self,proxy):
		self.proxy = proxy
		#self.driver = self.getDriver()
		#self.proxiedDriver = self.getProxiedDriver(proxy)
		pass
		
	def getProxiedDriver(self, proxy):
		service_args = [
			'--proxy=%s' %proxy,
			'--proxy-type=http',
			'--load-images=false'
			]
		return webdriver.PhantomJS(executable_path = '/usr/local/bin/phantomjs',desired_capabilities=self.dcap,service_args=service_args,)
	
	def getDriver(self):
		service_args = [
			'--load-images=false'
			]
		driver = webdriver.PhantomJS(executable_path = '/usr/local/bin/phantomjs',desired_capabilities=self.dcap,service_args=service_args,)
		return driver
	
	def __del__(self):
		#self.proxiedDriver.quit()
		#self.driver.quit()
		pass
		
	
	def requestByURL(self,url):
		driver = self.getDriver()
		try:
			driver.get(url)
			content = driver.page_source.encode('utf-8')
			return content
		except Exception as e: 
			errorStack = traceback.format_exc()
			logging.error('[PID:%s] PhantomJS request exception with url(%s)! exception info:%s'%(os.getpid(),url,errorStack))
			return None
		finally:
			driver.quit()

	def requestWithProxy(self,url):
		proxiedDriver = self.getProxiedDriver(self.proxy)
		try:
			proxiedDriver.get(url)
			content = proxiedDriver.page_source.encode('utf-8')
			return content
		except Exception as e: 
			print e
			errorStack = traceback.format_exc()
			logging.error('[PID:%s] PhantomJS request exception with url(%s) and proxy(%s)! exception info:%s'%(os.getpid(),url,self.proxy,errorStack))
			return None
		finally:
			proxiedDriver.quit()

if __name__ == '__main__':
	if len(sys.argv)>1:
		url = sys.argv[1]
	else:
		myurl = raw_input("Input an url:\n")
		if len(myurl.strip())>0:
			url = myurl.strip()
		else:
			print('Invalid input, exit..')
			sys.exit()
	phantomjs = PhantomJS()
	html1 = phantomjs.requestWithProxy(url,"81.95.182.31:80")
	f = file("page.html",'w')
	f.writelines(html1)
	f.close()
