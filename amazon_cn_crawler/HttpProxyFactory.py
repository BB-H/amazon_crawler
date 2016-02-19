# -*- coding: utf-8 -*-

import socket, time, thread, logging, os
import urllib2, threading
import threading
import random
import time
from multiprocessing.dummy import Pool as ThreadPool
#from phantomJsTool import PhantomJS as PhantomJSService


class HttpProxyFactory(object):
	
	TEST_PAGE_BING = "http://cn.bing.com/"
	TEST_PAGE_AMAZON = "http://www.amazon.cn/gp/site-directory"
	MAX_THREAD = 100
	allProxySet=set([#This is just an example, allProxySet will be restructured from proxy.list file in __init__()
		"23.94.37.50:3128",
		#"121.193.143.249:80",
		#"120.195.194.10:80",
		#"120.195.194.149:80",
		#"27.46.52.31:9797",
		#"58.251.47.101:8081",
		#"120.195.199.240:80",
		#"120.195.198.6:80",
		#"120.195.203.132:80",
		#"218.92.227.165:29037",
		#"120.195.192.83:80",
		#"60.191.153.75:3128",
		#"218.92.227.166:15275",
		#"120.195.195.71:80",
		#"110.73.1.241:8123",
		"182.90.80.80:8123",
		])
	validProxyList = []
	lock = threading.Lock()
	proxyLock = threading.Lock()
	__instance = None

	def __init__(self):
		proxyFile = os.path.join(os.getcwd(),"amazon_cn_crawler","proxy.list")
		if os.path.isfile(proxyFile):
			f = file(proxyFile, 'r')
			HttpProxyFactory.allProxySet = set()
			for line in f.readlines():
				line = line.strip()
				if len(line)>0:
					HttpProxyFactory.allProxySet.add(line)
			f.close()
		print("All proxies are:%s" % len(HttpProxyFactory.allProxySet))
		threadAmount = max(len(HttpProxyFactory.allProxySet)/5,2)
		threadAmount = min(threadAmount,HttpProxyFactory.MAX_THREAD)
		pool = ThreadPool(threadAmount)
		pool.map(self.checkProxyAvailable,HttpProxyFactory.allProxySet)
		pool.close() 
		pool.join()
		#logging.debug("All accessible proxy is:"+str(len(HttpProxyFactory.validProxyList)))
		print("Available proxies are %s" %len(HttpProxyFactory.validProxyList))
		
	
	
	def checkProxyAvailable(self,ipAndPort):
		try:
			for i in [1,2,3]: #Check avaliability for 3 times
				proxy_handler = urllib2.ProxyHandler({'http': ipAndPort})
				opener = urllib2.build_opener(proxy_handler)
				opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36')]
				urllib2.install_opener(opener)
				req=urllib2.Request(HttpProxyFactory.TEST_PAGE_AMAZON)
				req.add_header('Cache-Control', 'max-age=0')
				response = urllib2.urlopen(req,timeout=1.5)
				html = response.read()
				if html.find('id="nav-logo"')<0 and html.find("id='nav-logo'")<0: #amazon.cn login element
					return
				#if html.find('id="sb_form_go')<0: # html element in bing.com
					#return
				#print("Success! round.%s :%s" %(i,ipAndPort))
				time.sleep(2)
			HttpProxyFactory.proxyLock.acquire()
			print '[VALID] %s' % ipAndPort
			HttpProxyFactory.validProxyList.append(ipAndPort)
			HttpProxyFactory.proxyLock.release()
		except urllib2.HTTPError:
			print '[INVALID] %s' % ipAndPort
		except Exception:
			print '[INVALID] %s' % ipAndPort
	
	def getRandomProxy(self):
		proxy = None
		HttpProxyFactory.proxyLock.acquire()
		if len(HttpProxyFactory.validProxyList)>0:
			proxy = random.choice(HttpProxyFactory.validProxyList)
		logging.debug("Get a random Http proxy(1/%s):%s" %(len(HttpProxyFactory.validProxyList),str(proxy)))
		HttpProxyFactory.proxyLock.release()
		return proxy

		
	def getValidProxyAmount(self):
		return len(HttpProxyFactory.validProxyList)

	@staticmethod
	def getHttpProxyFactory():
		HttpProxyFactory.lock.acquire()
		if HttpProxyFactory.__instance is None:
			HttpProxyFactory.__instance = HttpProxyFactory()
		HttpProxyFactory.lock.release()
		return HttpProxyFactory.__instance


if __name__ == '__main__':
	factory = HttpProxyFactory()

	i=1
	for info in HttpProxyFactory.validProxyList:
		print "Output with proxy:"+info
		proxy_handler = urllib2.ProxyHandler({'http': info})
		opener = urllib2.build_opener(proxy_handler)
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		urllib2.install_opener(opener)
		req=urllib2.Request(HttpProxyFactory.TEST_PAGE_AMAZON)
		response = urllib2.urlopen(req,timeout=10)
		cont = response.read()
		f = file("page-%s.html" %i, 'w')
		f.write(cont)
		f.close()
		i+=1
	#for proxy in factory.allProxySet:
	#	a = threading.Thread(None, factory.is_OK, None, (proxy,), None)
	#	a.start()



