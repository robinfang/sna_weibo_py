#coding=utf-8
"""用于微博本身以及其转发详情的抓取。

"""
import urllib2
from lxml import etree
from StringIO import StringIO
import re
import lxml.html.soupparser as soupparser
import datetime
class WeiboPost(object):
    """一条新浪微博。
    Attributes:
        mid: 字符串，微博的mid，形如zAjoQmY0n
        uid: 字符串发布者id
        post_time: 发布时间
        content: 字符串内容
        repost_list: WeiboReply回复列表
    """
    def __init__(self, mid=None, uid=None, post_time=None, content=None):
        self.mid = mid
        self.uid = uid
        self.post_time = post_time
        self.content = content
class WeiboReply(object):
    """一条微博回复。
    Attributes:
        user_url: 字符串用户链接。
        content: 用户转发内容。
        repost_time: 用户转发时间。
    """
    def __init__(self, user_url=None, content=None, repost_time=None):
        self.user_url = user_url
        self.content = content
        self.repost_time = repost_time

def get_replys_list(url):
    """取得一个页面内的回复。
    Args:
        url: 页面的链接，包含page参数
    Returns: 
        一个list，其中的元素为WeiboReply类的实例
    """
    list = []
    
    
mid = "zAjoQmY0n"
gsid = "4uwgb764149TppfO8K622703C8g"
url = "http://weibo.cn/repost/"
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20100101 Firefox/21.0"}
request = urllib2.Request("%s%s?&gsid=%s"%(url,mid,gsid),headers=headers)
data = urllib2.urlopen(request).read()
f = open('repo.xml','w')
f.write(data)
f.close()
dom = soupparser.fromstring(data)
divs = dom.xpath("//*[@class='c']")
weibo_post = WeiboPost()
weibo_post.repost_list = []
for i in range(0,len(divs)):
    nodes  =  divs[i].xpath('node()')
    if len(nodes)==0:
        continue
    elif nodes[-1].tag!='span':
        continue
    weibo_reply = WeiboReply()
    full_url_string = "weibo.cn%s" % nodes[0].get('href')
    weibo_reply.user_url = full_url_string
    weibo_reply.user_url = re.compile(r'(\S*)?\?').match(full_url_string).group(1)
    print weibo_reply.user_url
    time_string = re.compile(ur'(.*)\u6765.*').match(nodes[-1].text).group(1).strip()
    print time_string
    time_string_split = time_string.split()
    if len(time_string_split)==1:
        minutes = re.compile(ur'(.*)\u5206.*').match(time_string_split[0]).group(1)    #取得转发距现在过去了几分钟
        #print minutes
        weibo_reply.repost_time = datetime.datetime.today()\
                +datetime.timedelta(minutes = 0-int(minutes))
       
    elif u'\u4eca\u5929' in time_string_split:
        time = time_string_split[1]    #取得转发时间HH:mm
        hour,minutes = time.split(":")
        today = datetime.date.today()
        weibo_reply.repost_time = datetime.datetime(today.year,\
                today.month,\
                today.day,\
                int(hour),int(minutes))
                
    print "repost_time : %s"%weibo_reply.repost_time
    weibo_post.repost_list.append(weibo_reply)
