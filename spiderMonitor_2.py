# -*- coding: utf-8 -*-
import os,time,datetime
#from collections import deque
import subprocess,signal,contextlib,warnings
import logging
from logging.handlers import RotatingFileHandler


MAX_FAILURE =3 
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
#fh.setFormatter(formatter)  
fh = RotatingFileHandler("spiderMonitor.log",maxBytes=20*1024*1024,backupCount=5)
ch.setFormatter(formatter)  
  
# 给logger添加handler  
logger.addHandler(fh)  
logger.addHandler(ch)  

process_start_time = datetime.datetime.now()
error_times = 0

def renewProcess(p):
	global error_times,process_start_time
	p.terminate()
	p.wait()
	try:
		os.killpg(p.pid, signal.SIGTERM)
	except OSError as e:
		logger.error(e)
	p = subprocess.Popen("scrapy crawl amazon_cn",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,preexec_fn=os.setsid)
	error_times = 0
	process_start_time = datetime.datetime.now()
	return p


#start = datetime.datetime.now()
p = subprocess.Popen("scrapy crawl amazon_cn",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,preexec_fn=os.setsid)
logger.info('Open a spider[PID:%s]..' %(p.pid))

i=0
while True:
	current = datetime.datetime.now()
	if (current-process_start_time).seconds>=60*60*1: #一小时重启一次
		logger.info('KILL a process [PID:%s] after an hour[%s]' %(p.pid,time.strftime(ISOTIMEFORMAT,time.localtime())))
		p = renewProcess(p)
		logger.info('Renew a process [PID:%s][%s]' %(p.pid,time.strftime(ISOTIMEFORMAT,time.localtime())))
	else:
		line = p.stdout.readline()
		#logger.debug(">>>[PID:%s]CURRENT LINE:%s" %(p.pid,line))
		if i%20==0:
			logger.debug("[PID:%s] [%s]Scanning..." %(p.pid,time.strftime(ISOTIMEFORMAT,time.localtime())))
		if line != '' or p.poll() == None:# 进程还没有结束
			#check the line
			if line.find('IndexError: list index out of range')>=0:
				error_times=error_times+1
				logger.info('Find an error with PID:%s, failure times:%s/%s' %(p.pid,error_times,MAX_FAILURE))
				if error_times>=MAX_FAILURE:
					logger.info('KILL a process [PID:%s] after failures [%s]' %(p.pid,time.strftime(ISOTIMEFORMAT,time.localtime())))
					p = renewProcess(p)
					logger.info('Renew a process [PID:%s][%s]' %(p.pid,time.strftime(ISOTIMEFORMAT,time.localtime())))
		else:
			logger.info("Process[PID:%s] closed from outside." %p.pid)
			break
		i+=1
		if i>10000:
			i=0
logger.info("[PID:%s] The END." %p.pid)
