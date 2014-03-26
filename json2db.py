#coding=utf-8
import os
import json
import MySQLdb
import codecs
import logging 
import hashlib
# 创建一个logger 
logger = logging.getLogger('weibo_crawler') 
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

def file2Db(filepath):
    """
        这里设计得太烂
    """
    file = codecs.open(filepath, mode = "r", encoding = 'utf-8') 
    s = json.load(file)
    try:
        conn = MySQLdb.connect(host = '222.199.193.19', user = 'root', passwd = 'root', port=3306, db='weibo')
        conn.set_character_set('utf8')
        cur = conn.cursor()
        mid = s["mid"]
        content = s["content"]
        time = s["time"]
        username = s["user_sname"]
        userurl = s["user_url"]
        repostlist= s["repost_list"]
        sqlstr = "insert ignore into user values(%s, %s)" 
        cur.execute(sqlstr, (username, userurl))
        sqlstr2 = "insert ignore into weibopost values(%s,%s,STR_TO_DATE(%s,'%%Y%%m%%d-%%H%%i'),%s)"
        cur.execute(sqlstr2, (mid, content, time, userurl))  
        for item in repostlist:
            username = item["user_sname"]
            userurl = item["user_url"]
            sqlstr3 = "insert ignore into user values(%s, %s)"
            cur.execute(sqlstr3, (username, userurl))
            repoststring = item["repost_string"].replace(u"\xa0","")
            time = item["time"]
            content = item["content"].replace(u"\xa0","")
            line = "%s%s%s" % (time, userurl, content)
            repostid = hashlib.md5(line.encode("utf-8")).hexdigest()[0:20]
            sqlstr4 = "insert ignore into repost values(%s, STR_TO_DATE(%s,'%%Y%%m%%d-%%H%%i'), %s, %s, %s ,%s)" 
            cur.execute(sqlstr4, (repostid, time, content, repoststring, userurl, mid))
        conn.commit()
        conn.close()
    except Exception, e:
        logger.error("Exception: %s", e)
        print cur._last_executed
        
    else:
        logger.info("SQL writed %s" % filepath)


if __name__ == "__main__":

    path = "../weibo_3_20_test"
    files = os.listdir(path)
    for i in files:
        filepath = "%s/%s" % (path, i)
        file2Db(filepath)