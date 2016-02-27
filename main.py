# -*- coding: utf-8 -*-
import os,time
#from collections import deque
import subprocess,signal,contextlib,warnings
import logging
from logging.handlers import RotatingFileHandler
import time

SPIDER_AMOUNT = 6
MAX_FAILURE =3 
processDict = {}
ISOTIMEFORMAT='%Y-%m-%d %X'

# 创建一个logger  
logger = logging.getLogger('spiderMonitor')  
logger.setLevel(logging.DEBUG)
# 创建一个handler，用于写入日志文件  
#fh = logging.FileHandler('spiderMonitor.log') 
fh = RotatingFileHandler("spiderMonitor.log",maxBytes=20*1024*1024,backupCount=5)

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
	p = subprocess.Popen("python ./spiderMonitor_2.py",shell=True)
	logger.info('[%s/%s]Open a spider Monitor[PID:%s]..' %(i+1,SPIDER_AMOUNT,p.pid))
	

