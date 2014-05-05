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
#logger.addHandler(fh) 
logger.addHandler(ch) 


def parseWeibo(mid):
    # 先判断mid是否处理过
    processed = listJson(outpath)
    if mid in processed:
        logger.info("passed %s" , mid)
        return
    wp = WeiboParser("http://weibo.cn/repost/%s" % mid)
    try:
        total_page = wp.getTotalPage(wp.weibo_url)
        if total_page > 3000:
            logger.warning("passed %s for too many pages", mid)
            append2Pass(mid)
            return # 由于抓取能力有限，暂时不处理3000页以上转评的微博
        weibopost = wp.getWeiboPost()
    except Exception, e:
        logger.error("Exception: %s", e)
        logger.warning("passed %s for Exception" , mid)
        append2Pass(mid)
        return
    else:
        weibopost.saveJSON()
def append2Pass(mid):
    file = open("passlist", "a")
    file.write("%s\n" % mid)
    file.close()
        
def listJson(path):
    filelist = os.listdir(path)
    processed = [i[0:-5] for i in filelist]
    return processed

if __name__ == "__main__":
    timeout = 20
    socket.setdefaulttimeout(timeout)
    global outpath
    outpath = "../weibo_3_20_test"
    processed = listJson(outpath) # 取得已经处理过的
    
    file = open("passlist","r")
    contents = file.readlines()
    for i in contents:
        processed.append(i.rstrip("\n")) # 将已处理的和跳过的合并得到所有需要跳过的
    file.close()
    
    file = open("midlist","r")
    midlist = []
    contents = file.readlines()
    for i in contents:
        midlist.append(i.rstrip("\n"))
    file.close()
    cleanlist = list(set(midlist).difference(set(processed))) # 待处理的和所有需要跳过的求差集
    pool = ThreadPool(4) 
    pool.map(parseWeibo, cleanlist) 
    pool.close()
    pool.join()
