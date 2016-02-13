# -*- coding: utf-8 -*-
#!/usr/bin/python
#from scrapy.http import HtmlResponse
#from scrapy.http import Request
import sys, os, logging, traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


if len(sys.argv)>1:
	url = sys.argv[1]
else:
	myurl = raw_input("Input an url:\n")
	if len(myurl.strip())>0:
		url = myurl.strip()
	else:
		logger.debug('Invalid input, exit..')
		sys.exit()

user_agent = (
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"
)

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = user_agent

#browser = webdriver.PhantomJS(desired_capabilities=dcap)
		
#service_args = ['--load-images=true', '--disk-cache=true',] 
driver = webdriver.PhantomJS(executable_path = '/usr/local/bin/phantomjs',desired_capabilities=dcap,)
try:
	driver.get(url)
	#wait = WebDriverWait(driver, 20)#设置超时时长
	#wait.until(EC.presence_of_element_located((By.ID, 'ourprice_shippingmessage')))#直到agsBadge元素被填充之后才算请求完成
	
	content = driver.page_source.encode('utf-8')
	f = file('page.html','w')
	f.writelines(content)
	f.close()
	print "SUCCESS!"
except Exception as e: 
	print e
	errorStack = traceback.format_exc()
	logging.error('[PID:%s] PhantomJS request exception! exception info:%s'%(os.getpid(),errorStack))
	print "FAILED!"
finally:
	driver.quit()