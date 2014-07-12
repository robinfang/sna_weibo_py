#coding=utf-8
from weibo_crawler import *
import os
import fnmatch
import logging 
import MySQLdb
import codecs
from multiprocessing.dummy import Pool as ThreadPool 

# 创建一个logger 
logger = logging.getLogger('multi_crawler_u2m') 
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
path = yamlconfig["input"]["userdir"] # 存放用户url的文件夹路径
outpath = yamlconfig["output"]["simpleweibodir"] # 存放输出微博文本的文件夹路径
gsidstack = yamlconfig["input"]["gsidstack"]
donelist = yamlconfig["output"]["done"] # 存放处理过的url的文件路径
"""
def getMid(filepath):
    logger.info("calling getMid")
    file = open(filepath)
    all_text = file.readlines()
    file.close()
    for j in all_text:
        url = j.strip().split(",")[1]
        logger.info("User url: %s", url)
        up = UserParser(url)
        weibolist = []
        weibolist = up.get_weibolist(1)
        #midlist = up.get_midlist(20) # 每个用户取前多少页
        

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
   
"""
def getWeibo(user_url):
    up = UserParser(gsidstack, user_url)
    weibolist = up.get_weibolist(3)
    filename ="%s/weibo.%s" % (outpath, up.uid)
    f =  codecs.open(filename, mode = "w", encoding = 'utf-8')
    for i in weibolist:
        # logger.info("id: %s", i["id"])
        oneline = "org:%s %s %s %s %s %s %s\n" % (i["id"], i["name"], i["nick"], i["repost"], i["comment"], i["from"], i["timestamp"])
        f.write(oneline)
        f.write("content:%s\n" % i["content"])
    logger.info("user %s done" % user_url)
    f.close()
    f = open(donelist, "a")
    f.write(" ,%s\n" % user_url)
    f.close()
def getUrlList(filepath): #从文件中取得url的列表
    file = open(filepath)
    all_text = file.readlines()
    file.close()
    result = []
    for j in all_text:
        url = j.strip().split(",")[1]
        result.append(url)
    return result
if __name__ == "__main__":

    timeout = 20
    socket.setdefaulttimeout(timeout)
    filelist = []
    files = os.listdir(path)
    for name in files:
        if fnmatch.fnmatch(name, "*.txt"):
            filelist.append(os.path.join(path, name))
    url_list = []
    for i in filelist:
        url_list.extend(getUrlList(i))
    done_list = getUrlList(donelist)
    target_list = list(set(url_list).difference(set(done_list))) 
    logger.info("%d urls to be parsed.", len(target_list))
    #getWeibo(url_list[0])
    pool = ThreadPool(2) 
    pool.map(getWeibo, target_list) 
    pool.close()
    pool.join()
    