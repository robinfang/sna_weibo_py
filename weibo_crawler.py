#coding=utf-8
import urllib2
from lxml import etree
from StringIO import StringIO
import re
import lxml.html.soupparser as soupparser
import datetime

class User(object):
    """微博用户
    
    Attributes:
        url: 用户url
        uid: 用户id
        following_number: 用户关注数 
        follower_number: 用户粉丝数
        sex: 性别
        age: 年龄
        tags: 标签
    """
    def __init__(self, uid = None, following_number = None,\
            follower_number = None, sex = None, age = None,\
            tags = None):
        self.uid = uid
        self.following_number = following_number
        self.follower_number = follower_number
        self.sex = sex
        self.age = age
        self.tags = tags
    
class WeiboPost(object):
    """一条新浪微博。
    
    Attributes:
        mid: 字符串，微博的mid，形如zAjoQmY0n
        user: 发布者
        post_time: 发布时间
        content: 字符串内容
        repost_list: WeiboReply回复列表
    """
    def __init__(self, mid = None, user = None, post_time = None, content = None):
        self.mid = mid
        self.user = user
        self.post_time = post_time
        self.content = content

class WeiboRepost(object):
    """一条微博回复。
    
    Attributes:
        content: 内容
        time: 时间
        user: 发布者
        from_user: 转发来源
    """
    def __init__(self, content = None, time = None, user = None, from_user = None):
        self.content = content
        self.time = time
        self.user = user
        self.from_user = from_user

class Parser(object):
    """

    Attributes:
        HEADERS: 请求头
        GSID: 微博免登录参数
    """
    HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20100101 Firefox/21.0"}
    GSID = "st=f17a&gsid=4u8p32bd1TPK1AXgrkUqT703C8g&vt=4"
    #GSID = "gsid=4u8p32bd1TPK1AXgrkUqT703C8g"
    def url2Dom(self, url):
        request = urllib2.Request(url, headers = self.HEADERS)
        data = urllib2.urlopen(request).read()
        dom = soupparser.fromstring(data)
        return dom
    def parseTime(self, time_string):
        time_string_split = time_string.split()
        print "time_string: %s" % time_string
        match_ymd = re.compile(ur'(\d{4})-(\d{2})-(\d{2})').match(time_string_split[0])
        if len(time_string_split) == 1:
            print "case1: xx ago"
            minutes = re.compile(ur'(.*)\u5206.*').match(time_string_split[0]).group(1) # 取得转发距现在过去了几分钟
            time = datetime.datetime.today()\
                +datetime.timedelta(minutes = 0-int(minutes)) # 时间赋值
        elif u'\u4eca\u5929' in time_string_split:
            print "case2: today xxx"
            time = time_string_split[1] # 取得转发时间HH:mm
            hour,minutes = time.split(":")
            today = datetime.date.today()
            time = datetime.datetime(today.year,\
                today.month,\
                today.day,\
                int(hour),int(minutes))
        elif u'\u6708' in time_string_split[0] and u'\u65e5' in time_string_split[0]:
            print "case3: xx (Month) xx (Day)"
            date_string = time_string_split[0]
            match = re.compile(ur'(\d{2}).*(\d{2}).*').match(date_string)
            today = datetime.date.today()
            month = match.group(1)
            day = match.group(2)
            time = time_string_split[1]
            hour,minutes = time.split(":")
            time = datetime.datetime(today.year,\
                    int(month),\
                    int(day),\
                    int(hour),int(minutes))
        elif match_ymd != None:
            print "case4: xxxx-xx-xx xx:xx:xx"
            year = match_ymd.group(1)
            month = match_ymd.group(2)
            day = match_ymd.group(3)
            ltime = time_string_split[1]
            hour,minutes,_ = ltime.split(":")
            time = datetime.datetime(int(year),\
                    int(month),\
                    int(day),\
                    int(hour),int(minutes))
        return time
class UserParser(Parser):
    """
        
    Attributes:
        user_url: 用户链接
    """
    def __init__(self, user_url):
        self.user_url = user_url
    def getUser(self):
        user = User()
        url = "%s?%s" % (self.user_url, self.GSID)
        print url
        dom = self.url2Dom(url)
        uidstr = dom.xpath("//div[@class='tip2']/a")[0].get('href')
        user.uid = uidstr.split('/')[1] #用户数字id
        f = dom.xpath("//div[@class='tip2']/a") 
        followingstr =  f[0].text
        p = re.compile(ur'\S*\[(\d+)\]')
        followingu = p.match(followingstr).group(1)
        user.following_number = int(followingu) # 用户关注数  
        followerstr = f[1].text
        followeru = p.match(followerstr).group(1)
        user.follower_number = int(followeru) # 用户粉丝数
        print user.__dict__
        return user 

class WeiboParser(Parser):
    """
    
    Attributes： 
        weibo_url: 链接
    """
    def __init__(self, weibo_url):
        self.weibo_url = weibo_url
    def getWeiboPost(self):
        """解析
        """
        weibopost = WeiboPost()
        url = "%s?%s" % (self.weibo_url, self.GSID)
        # 微博mid
        weibopost.mid =  re.compile(r"\S*repost/(\S+)\?").match(url).group(1)
        dom = self.url2Dom(url)
        div = dom.xpath("//div[@id='M_']")[0] 
        user_url = "http://weibo.cn%s" % div.xpath("*/a")[0].get("href").split("?")[0]
        print "user_url: %s" % user_url
        userparser = UserParser(user_url)
        weibopost.user = userparser.getUser() # 微博发布者
        contentlist = div.xpath("*//span[@class='ctt']")[0].xpath("node()")
        strlist = []
        for cj in contentlist:
            if isinstance(cj,(unicode,str)):
                strlist.append(cj)
        weibopost.content = "".join(strlist) # 微博内容
        time_string =  div.xpath("*//span[@class='ct']")[0].text
        weibopost.post_time = self.parseTime(time_string) # 微博发布时间
        repost_list = self._getReposts(url)
        weibopost.repost_list = repost_list # repost_list
        print weibopost.__dict__ 
        return weibopost
    def _getReposts(self, url):
        """

        """
        repost_list = []
        lastpage = self._getTotalPage(url)
        print "lastpage: %d" % lastpage
        i = lastpage
        j = 1
        while i != 1:
            print "    j: %d" % j
            full_url = "%s&page=%d" % (url,i)
            print "full_url: %s" % full_url
            one_page = self._parseRepost(full_url)
            repost_list.extend(one_page)
            lastpage = self._getTotalPage(url)
            i = lastpage - j
            j += 1
        return repost_list
    def _getTotalPage(self, url):
        dom = self.url2Dom(url)
        page_string = dom.xpath("//*[@id='pagelist']/form/div/text()")[-1]
        # 注意，此处并未考虑转发不足一页的情况
        page_number = int(re.compile(r".*\d+/(\d+)").match(page_string).group(1)) # 匹配页码并转成int型
        return page_number
    def _parseRepost(self, url):
        reposts = []
        dom = self.url2Dom(url)
        divs = dom.xpath("//div[@class='c']")
        for i in range(0, len(divs)):
            nodes = divs[i].xpath("node()") # 一个nodes对应一行内容
            # 过滤掉两个不是回复的
            if len(nodes) == 0:
                continue
            elif nodes[-1].tag != 'span':
                continue
            weibo_repost = WeiboRepost()
            full_url_string = "http://weibo.cn%s" % nodes[0].get('href')
            user_url = full_url_string.split("?")[0]
            userparser = UserParser(user_url)
            weibo_repost.user = userparser.getUser() # 发布者
            # 从一行中遍历出内容和转发来源
            for j in range(0, len(nodes)):
                if isinstance(nodes[j],(unicode,str)):
                    content = nodes[j]
                    weibo_repost.content = content # 转发评论的内容
                    if content.endswith(u"//"):
                        f = j + 1
                        from_full_url = nodes[f].get("href") # 取得转发来源用户完整url
                        from_user_url = from_full_url.split("?")[0] # 取得转发
                        userparser = UserParser(from_user_url)
                        weibo_repost.from_user = userparser.getUser() # 转发来源
                    break
            time_string = re.compile(ur'(.*)\u6765.*').match(nodes[-1].text).group(1).strip()
            weibo_repost.time = self.parseTime(time_string) # 转发时间
            reposts.append(weibo_repost)
        return reposts
def getRepostList(url):
    """
    """
        
        
def getReplies(url):
    """以list形式通过url取得一个页面内的回复。
    
    Args:
        url: 页面的链接字符串，包含page参数、gsid、mid等，形如：http://weibo.cn/repost/yci8hkTUf?&gsid=4uwgb764149TppfO8K622703C8g&page=2
    Returns: 
        一个list，其中的元素为WeiboReply类的实例
    """
    list = []
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20100101 Firefox/21.0"}
    request = urllib2.Request(url,headers = headers)
    data = urllib2.urlopen(request).read()
    dom = soupparser.fromstring(data)
    divs = dom.xpath("//*[@class='c']")
    global gdivs
    gdivs = divs
    for i in range(0,len(divs)):
        nodes  =  divs[i].xpath('node()')
        if len(nodes)==0:
            continue
        elif nodes[-1].tag!='span':
            continue
        weibo_repost = WeiboRepost()
        for j in range(0,len(nodes)):
            if isinstance(nodes[j],(unicode,str)):
                content = nodes[j]
                #print type(content)
                #print "content:",content
                weibo_repost.content = content
                if content.endswith(u"//"):
                   f = j+1
                   from_url_string = nodes[f].get('href')
                   weibo_repost.from_user_url = re.compile(r'http://(\S*)?\?').match(from_url_string).group(1)
                   print "from_url: %s" % weibo_repost.from_user_url
                break
             
        full_url_string = "weibo.cn%s" % nodes[0].get('href')

        weibo_repost.user_url = re.compile(r'(\S*)?\?').match(full_url_string).group(1)
        print "user url:" + weibo_repost.user_url
        time_string = re.compile(ur'(.*)\u6765.*').match(nodes[-1].text).group(1).strip()
        print "time string:" + time_string
        time_string_split = time_string.split()
        match_ymd = re.compile(ur'(\d{4})-(\d{2})-(\d{2})').match(time_string_split[0])
        if len(time_string_split)==1:
            print "case1"
            minutes = re.compile(ur'(.*)\u5206.*').match(time_string_split[0]).group(1)    #取得转发距现在过去了几分钟
            #print minutes
            weibo_repost.repost_time = datetime.datetime.today()\
                    +datetime.timedelta(minutes = 0-int(minutes))

        elif u'\u4eca\u5929' in time_string_split:
            print "case2"
            time = time_string_split[1]    #取得转发时间HH:mm
            hour,minutes = time.split(":")
            today = datetime.date.today()
            weibo_repost.repost_time = datetime.datetime(today.year,\
                    today.month,\
                    today.day,\
                    int(hour),int(minutes))
        elif u'\u6708' in time_string_split[0] and u'\u65e5' in time_string_split[0]:
            print "case3"
            date_string = time_string_split[0]
            match = re.compile(ur'(\d{2}).*(\d{2}).*').match(date_string)
            today = datetime.date.today()
            month = match.group(1)
            day = match.group(2)
            time = time_string_split[1]
            hour,minutes = time.split(":")
            #print "nomth,day : %s, %s "% (month,day)
            weibo_repost.repost_time = datetime.datetime(today.year,\
                    int(month),\
                    int(day),\
                    int(hour),int(minutes))
        elif match_ymd!=None:
            print "case4"
            year = match_ymd.group(1)
            month = match_ymd.group(2)
            day = match_ymd.group(3)
            #print "year-month-day:%s,%s,%s"%(year,month,day)
            time = time_string_split[1]
            hour,minutes,_ = time.split(":")
            weibo_repost.repost_time = datetime.datetime(int(year),\
                    int(month),\
                    int(day),\
                    int(hour),int(minutes))
        print "repost_time: %s" % weibo_repost.repost_time
        print "content: %s" % weibo_repost.content
        list.append(weibo_repost)
    return list
    
if __name__ == "__main__":
    wp = WeiboParser("http://weibo.cn/repost/A5CPSEH0r")
    weibopost = wp.getWeiboPost()
