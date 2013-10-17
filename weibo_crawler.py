#coding=utf-8
import urllib2
from lxml import etree
from StringIO import StringIO
import re
import lxml.html.soupparser as soupparser
import datetime
import time
import json
import codecs
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
        user_url: 转发者url
        user_sname: 用户显示昵称
    """
    def __init__(self, mid = None, user = None, post_time = None, content = None):
        self.mid = mid
        self.user = user
        self.post_time = post_time
        self.content = content
    def toJSON(self):
        obj = {}
        obj['mid'] = self.mid
        obj['user_sname'] = self.user_sname
        obj['user_url'] = self.user_url
        obj['content'] = self.content
        obj['repost_list'] = []
        for j in self.repost_list:
            rp = {}
            rp['user_sname'] = j.user_sname
            rp['user_url'] = j.user_url
            rp['content'] = j.content
            if hasattr(j,"from_user_sname"): 
                rp['from_user_sname'] = j.from_user_sname
                rp['from_user_url'] = j.from_user_url
            rp['time'] =  j.time.strftime("%Y%m%d-%H%M")
            obj['repost_list'].append(rp)
        return obj
    def saveJSON(self):
        jstr = self.toJSON()
        filename = "weibo/%s.json" % self.mid
        with codecs.open(filename, mode = "w", encoding = 'utf-8') as f:
            json.dump(jstr, f)
class WeiboRepost(object):
    """一条微博回复。
    
    Attributes:
        content: 内容
        time: 时间
        user: 转发者
        from_user: 转发来源
        user_url: 转发者链接
        from_user_url: 转发来源url
        user_sname: 转发用户昵称
        from_user_sname: 来源用户昵称
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
        gsid: 微博免登录参数
    """
    HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20100101 Firefox/21.0"}
    gsid = ""
    gsidstack = ["gsid=4um81d481ws9jVfW65fHRfNr36t",\
            "gsid=4ukd1d481tNHjEDK1cdd5fO7L2W",\
            "gsid=4u8p32bd1TPK1AXgrkUqT703C8g",\
            "gsid=4u2g32bd14l1bYh2F0pMG9IF08T",\
            "gsid=4uAE32bd1xCJhrVSl3HSVfOyUcU",\
            "gsid=4up432bd1YQRUWIdjKzaNfOzh70",\
            "gsid=4ucN32bd1ixLWJtnd3ajlfRRm5x",\
            "gsid=4uVA7ef41UxFjVNCfTEOufRRp2V",\
            "gsid=4un632bd160jDyV25wbFmf8Qu01",\
            "gsid=4uJr32bd1L2uQ2xzEhwFYfV3b07",\
            "gsid=4uNl32bd1xXvVO17TtHcnfV3h86",\
            "gsid=4urP32bd1q2mbPq45m58wf9YVfh",\
            "gsid=4u8U32bd1TARFS6LWDhBaf8Qvec",\
            "gsid=4ufT32bd1o0yXUtGhlTZhfUcM4S",\
            "gsid=4uar32bd1VgX4Hg84LR2ifUcQdi",\
            "gsid=4uOV32bd1h3r9ckdjJSf6fUWs4g"
            ]
    def popGsid(self):
        self.gsid = self.gsidstack.pop()
    def url2Dom(self, url):
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
        request = urllib2.Request(url, headers = self.HEADERS)
        data = urllib2.urlopen(request).read()
        dom = soupparser.fromstring(data)
        return dom
    def parseTime(self, time_string):
        time_string_split = time_string.split()
        # print "time_string: %s" % time_string
        match_ymd = re.compile(ur'(\d{4})-(\d{2})-(\d{2})').match(time_string_split[0])
        if len(time_string_split) == 1:
            # print "case1: xx ago"
            minutes = re.compile(ur'(.*)\u5206.*').match(time_string_split[0]).group(1) # 取得转发距现在过去了几分钟
            time = datetime.datetime.today()\
                +datetime.timedelta(minutes = 0-int(minutes)) # 时间赋值
        elif u'\u4eca\u5929' in time_string_split:
            # print "case2: today xxx"
            time = time_string_split[1] # 取得转发时间HH:mm
            hour,minutes = time.split(":")
            today = datetime.date.today()
            time = datetime.datetime(today.year,\
                today.month,\
                today.day,\
                int(hour),int(minutes))
        elif u'\u6708' in time_string_split[0] and u'\u65e5' in time_string_split[0]:
            # print "case3: xx (Month) xx (Day)"
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
            # print "case4: xxxx-xx-xx xx:xx:xx"
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
        self.popGsid()
        self.user_url = user_url
    def getUser(self):
        user = User()
        url = "%s?%s" % (self.user_url, self.gsid)
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
        self.popGsid()
        self.weibo_url = weibo_url
    def getWeiboPost(self):
        """解析
        """
        weibopost = WeiboPost()
        url = "%s?%s" % (self.weibo_url, self.gsid)
        # 微博mid
        weibopost.mid =  re.compile(r"\S*\w+/(\S+)\?").match(url).group(1)
        dom = self.url2Dom(url)
        div = dom.xpath("//div[@id='M_']")[0] 
        user_url = "http://weibo.cn%s" % div.xpath("*/a")[0].get("href").split("?")[0]
        user_sname = div.xpath("*/a")[0].text
        weibopost.user_sname = user_sname # 微博发布者昵称
        print "user_url: %s" % user_url
        #userparser = UserParser(user_url)
        #weibopost.user = userparser.getUser() # 微博发布者
        weibopost.user_url = user_url #微博发布者链接
        contentlist = div.xpath("*//span[@class='ctt']")[0].xpath("node()")
        strlist = []
        for cj in contentlist:
            if isinstance(cj,(unicode,str)):
                strlist.append(cj)
        weibopost.content = "".join(strlist) # 微博内容
        time_string =  div.xpath("*//span[@class='ct']")[0].text
        weibopost.post_time = self.parseTime(time_string) # 微博发布时间
        repost_list = self._getReposts(self.weibo_url) # 此处传递的是不带参数的
        weibopost.repost_list = repost_list
        print weibopost.__dict__ 
        return weibopost
    def _getReposts(self, weibo_url):
        """

        """
        global repost_list 
        repost_list = []
        lastpage = self._getTotalPage(weibo_url+"?"+self.gsid)
        i = lastpage
        j = 1
        while i != 0:
            if i%200 == 0:
                try: 
                    self.popGsid()
                except:
                    print "No more gsid!"
            print "    j: %d    i:%d" % (j,i)
            full_url = "%s?%s&page=%d" % (weibo_url,self.gsid,i)
            print "full_url: %s" % full_url
            page_number, one_page = self._parseRepost(full_url)
            repost_list.extend(one_page)
            i = page_number - j
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
        page_string = dom.xpath("//*[@id='pagelist']/form/div/text()")[-1]
        # 注意，此处并未考虑转发不足一页的情况
        page_number = int(re.compile(r".*\d+/(\d+)").match(page_string).group(1)) # 匹配页码并转成int型
        divs = dom.xpath("//div[@class='c']")
        for i in range(0, len(divs)):
            nodes = divs[i].xpath("node()") # 一个nodes对应一行内容
            # 过滤掉两个不是回复的
            if len(nodes) == 0:
                continue
            elif nodes[-1].tag != 'span':
                continue
            # 取得一行内容文本
            a_line = "".join(divs[i].xpath("text()"))
            text_list.append(a_line)
            weibo_repost = WeiboRepost()
            full_url_string = "http://weibo.cn%s" % nodes[0].get('href')
            user_url = full_url_string.split("?")[0]
            weibo_repost.user_url = user_url # 转发者url
            user_sname = nodes[0].text # 转发者昵称
            weibo_repost.user_sname = user_sname
            #userparser = UserParser(user_url)
            #weibo_repost.user = userparser.getUser() # 发布者
            # 从一行中遍历出内容和转发来源
            for j in range(0, len(nodes)):
                if isinstance(nodes[j],(unicode,str)):
                    content = unicode(nodes[j])
                    weibo_repost.content = content # 转发评论的内容
                    if content.endswith(u"//"):
                        f = j + 1 
                        # 这里如果出现内容以//结尾但是没有转发来源的会出现问题
                        from_full_url = nodes[f].get("href") # 取得转发来源用户完整url
                        from_user_url = from_full_url.split("?")[0] # 取得转发者链接
                        #userparser = UserParser(from_user_url)
                        #weibo_repost.from_user = userparser.getUser() # 转发来源
                        weibo_repost.from_user_url = from_user_url
                        from_user_sname = nodes[f].text.lstrip("@") # 需去除'@'符号
                        weibo_repost.from_user_sname = from_user_sname # 转发来源昵称
                    break
            time_string = re.compile(ur'(.*)\u6765.*').match(nodes[-1].text).group(1).strip()
            weibo_repost.time = self.parseTime(time_string) # 转发时间
            reposts.append(weibo_repost)
        return page_number, reposts

if __name__ == "__main__":
    wp = WeiboParser("http://weibo.cn/repost/AbZtR9AZS")
    global text_list
    text_list = []
    weibopost = wp.getWeiboPost()
    weibopost.saveJSON()
