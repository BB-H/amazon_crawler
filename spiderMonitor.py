# -*- coding: utf-8 -*-
import os,time
#from collections import deque
import subprocess
import logging
import time

SPIDER_AMOUNT = 2
MAX_FAILURE = 10
process_list = []
processDict = {}
ISOTIMEFORMAT='%Y-%m-%d %X'

# 创建一个logger  
logger = logging.getLogger('spiderMonitor')  
logger.setLevel(logging.DEBUG)
# 创建一个handler，用于写入日志文件  
fh = logging.FileHandler('spiderMonitor.log')  
fh.setLevel(logging.DEBUG)
# 再创建一个handler，用于输出到控制台  
ch = logging.StreamHandler()  
ch.setLevel(logging.DEBUG) 
# 定义handler的输出格式  
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
fh.setFormatter(formatter)  
ch.setFormatter(formatter)  
  
# 给logger添加handler  
logger.addHandler(fh)  
logger.addHandler(ch)  

for i in range(0,SPIDER_AMOUNT):
	logger.info('[%s/%s]Open a spider..' %(i+1,SPIDER_AMOUNT))
	p = subprocess.Popen("scrapy crawl amazon_cn",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	#process_list.append(p)
	processDict[p] = 0

i=0
while True:
	for p,_ in processDict.items():
		line = p.stdout.readline() 
		if i%20==0:
			print "[%s] Scanning [PID:%s]..." %(time.strftime(ISOTIMEFORMAT,time.localtime()),p.pid)
		if line != '' or p.poll() == None:# 进程还没有结束
			#check the line
			if line.find('IndexError: list index out of range')>=0:
				logger.debug('Find an error with PID:%s' %p.pid)
				processDict[p]=processDict[p]+1
				if processDict[p]>=MAX_FAILURE:
					logger.info('KILL a process [PID:%s]' %p.pid)
					p.terminate()
					del processDict[p]
					newP = subprocess.Popen("scrapy crawl amazon_cn",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
					processDict[newP] = 0
					logger.info('Renew a process [PID:%s]' %newP.pid)
		else:
			del processDict[p]
			newP = subprocess.Popen("scrapy crawl amazon_cn",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			processDict[newP] = 0
			logger.info('PID(%s) is killed, renew a process [PID:%s]' %(p.pid,newP.pid))
	i+=1
	if i>10000:
		i=0
print "The END."
