#coding=utf-8
from weibo_crawler import *
import os
import fnmatch
import logging 
import MySQLdb
from multiprocessing.dummy import Pool as ThreadPool 

# 创建一个logger 
logger = logging.getLogger('mylogger') 
logger.setLevel(logging.DEBUG) 
   
# 创建一个handler，用于写入日志文件 
fh = logging.FileHandler('test.log') 
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


path = "prepare"

def getMid(filepath):
    print "getMid"
    file = open(filepath)
    all_text = file.readlines()
    file.close()
    for j in all_text:
        url = j.strip().split(",")[1]
        logger.info("User url: %s", url)
        up = UserParser(url)
        midlist = []
        midlist = up.get_midlist(20) # 每个用户取10页
        try:
            conn = MySQLdb.connect(host = 'localhost', user = 'root', passwd = '', port=3306, db='sn_weibo')
            cur = conn.cursor()    
            cur.executemany("insert into mids values(%s)", midlist)
            conn.commit()
            conn.close()
        except Exception, e:
            logger.error("Exception: %s", e)
        else:
            logger.info("SQL writed %s" % filepath)
if __name__ == "__main__":
    timeout = 20
    socket.setdefaulttimeout(timeout)
    filelist = []
    files = os.listdir(path)
    for name in files:
        if fnmatch.fnmatch(name, "*.txt"):
            filelist.append(os.path.join(path, name))
    pool = ThreadPool(4) 
    pool.map(getMid, filelist) 
    pool.close()
    pool.join()
    