#coding=utf-8
import logging 
from multiprocessing.dummy import Pool as ThreadPool 
import socket
import os
from weibo_crawler import *
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


def parseWeibo(mid):
    # 先判断mid是否处理过
    filelist = os.listdir(outpath)
    processed = [i[0:-5] for i in filelist]
    if mid in processed:
        logger.info("passed %s" , j)
        return
    wp = WeiboParser("http://weibo.cn/repost/%s" % mid)
    try:
        total_page = wp.getTotalPage(wp.weibo_url)
        if total_page > 3000:
            return # 由于抓取能力有限，暂时不处理3000页以上转评的微博
            logger.warning("passed %s for too many pages", mid)
        weibopost = wp.getWeiboPost()
    except Exception, e:
        logger.error("Exception: %s", e)
        logger.warning("passed %s for Exception" , mid)
        return
    else:
        weibopost.saveJSON()


if __name__ == "__main__":
    timeout = 20
    socket.setdefaulttimeout(timeout)
    global outpath
    outpath = "../weibo_3_20_test"
    file = open("midlist","r")
    midlist = []
    contents = file.readlines()
    for i in contents:
        midlist.append(i.rstrip("\n"))
    file.close()
    pool = ThreadPool(4) 
    pool.map(parseWeibo, midlist) 
    pool.close()
    pool.join()
