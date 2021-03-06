# -*- coding: utf-8 -*-
import os,time
#from collections import deque
import subprocess,signal,contextlib,warnings
import logging
import time

SPIDER_AMOUNT = 1
MAX_FAILURE =3 
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
	p = subprocess.Popen("scrapy crawl amazon_cn",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,preexec_fn=os.setsid)
	logger.info('[%s/%s]Open a spider[PID:%s]..' %(i+1,SPIDER_AMOUNT,p.pid))
	processDict[p] = 0

i=0
while True:
	for p,_ in processDict.items():
		line = p.stdout.readline()
		print(">>>[PID:%s]CURRENT LINE:%s" %(p.pid,line))
		if i%20==0:
			logger.debug("[%s] Scanning [PID:%s]..." %(time.strftime(ISOTIMEFORMAT,time.localtime()),p.pid))
		if line != '' or p.poll() == None:# 进程还没有结束
			#check the line
			
			if line.find('IndexError: list index out of range')>=0 or line.find('Spider error processing <GET')>=0 or line.find('Traceback (most recent call last)')>=0:
				processDict[p]=processDict[p]+1
				logger.debug('Find an error with PID:%s, failure times:%s/%s' %(p.pid,processDict[p],MAX_FAILURE))
				if processDict[p]>=MAX_FAILURE:
					logger.info('KILL a process [PID:%s]' %p.pid)
					p.terminate()
					p.wait()
					try:
						os.killpg(p.pid, signal.SIGTERM)
					except OSError as e:
						logger.error(e)
					del processDict[p]
					newP = subprocess.Popen("echo 'Sleep a while before start new spider';sleep 1m;scrapy crawl amazon_cn",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,preexec_fn=os.setsid)
					processDict[newP] = 0
					logger.info('Renew a process [PID:%s]' %newP.pid)
		else:
			continue
			'''
			del processDict[p]
			newP = subprocess.Popen("scrapy crawl amazon_cn",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,preexec_fn=os.setsid)
			processDict[newP] = 0
			logger.info('PID(%s) is killed, renew a process [PID:%s]' %(p.pid,newP.pid))
			'''
	i+=1
	if i>10000:
		i=0
print "The END."
