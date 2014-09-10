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


f = open("config.yaml")
yamlconfig  = yaml.load(f) # 配置文件
f.close()
outpath =  yamlconfig["output"]["weibodir"]
passed = yamlconfig["output"]["passed"]
midlistpath = yamlconfig["input"]["midlist"] 
gsidstack = yamlconfig["input"]["gsidstack"]

def parseWeibo(mid):
    # 先判断mid是否处理过
    wp = WeiboParser(gsidstack, "http://weibo.cn/repost/%s" % mid)
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
        weibopost.saveJSON(outpath)
def append2Pass(mid):
    file = open(passed, "a")
    file.write("%s\n" % mid)
    file.close()
        
def listJson(path):
    filelist = os.listdir(path)
    processed = [i[0:-5] for i in filelist]
    return processed

if __name__ == "__main__":
    timeout = 20
    socket.setdefaulttimeout(timeout)
    # global outpath
    # outpath = "../weibo_test"
    checkfile(passed)
    checkdir(outpath)
    processedlist = listJson(outpath) # 取得已经处理过的
    f = open(passed,"r") # 取得跳过的
    passedlist = f.read().splitlines() 
    f.close()
    processedlist.extend(passedlist) # 合并跳过的和已经处理过的
    f = open(midlistpath,"r")
    midlist = f.read().splitlines()
    f.close()
    cleanlist = list(set(midlist).difference(set(processedlist))) # 待处理的和所有需要跳过的求差集
    pool = ThreadPool(4) 
    pool.map(parseWeibo, cleanlist) 
    pool.close()
    pool.join()
