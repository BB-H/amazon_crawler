# -*- coding: utf-8 -*-
#!/usr/bin/python
#from scrapy.http import HtmlResponse
#from scrapy.http import Request
import sys, os, logging, traceback
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class PhantomJS(object):
	
	user_agent = (
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"
	)
	
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap["phantomjs.page.settings.userAgent"] = user_agent
	
	def requestByURL(self,url):
		if url is None or url.strip()=="":
			return ""
		service_args = [
			'--load-images=false'
			]
		driver = webdriver.PhantomJS(executable_path = '/usr/local/bin/phantomjs',desired_capabilities=self.dcap,service_args=service_args,)
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

	def requestWithProxy(self,url,proxyinfo):
		service_args = [
			'--proxy=%s' %proxyinfo,
			'--proxy-type=http',
			'--load-images=false'
			]
		myDriver = webdriver.PhantomJS(executable_path = '/usr/local/bin/phantomjs',desired_capabilities=self.dcap,service_args=service_args,)
		try:
			myDriver.get(url)
			content = myDriver.page_source.encode('utf-8')
			return content
		except Exception as e: 
			print e
			errorStack = traceback.format_exc()
			logging.error('[PID:%s] PhantomJS request exception with url(%s) and proxy(%s)! exception info:%s'%(os.getpid(),url,proxyinfo,errorStack))
			return None
		finally:
			myDriver.quit()

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
