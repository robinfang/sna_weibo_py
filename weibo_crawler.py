#coding=utf-8
import urllib2
from lxml import etree
import re
import lxml.html.soupparser as soupparser
import datetime
import time as tm
import json
import codecs
import os
import logging 
import socket
import yaml
import sbase62 as sb
import calendar

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
logger.addHandler(fh) 
logger.addHandler(ch) 

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
        user_url: 发者url
        user_sname: 用户显示昵称
    """
    def __init__(self, mid = None, user = None, post_time = None, content = None):
        self.mid = mid
        self.user = user
        self.post_time = post_time
        self.content = content 
        self.repost_list = []
    def toJSON(self):
        obj = {}
        obj['mid'] = self.mid
        obj['user_sname'] = self.user_sname
        obj['user_url'] = self.user_url
        obj['content'] = self.content
        obj['time'] = self.post_time.strftime("%Y%m%d-%H%M")
        obj['repost_list'] = []
        for j in self.repost_list:
            rp = {}
            rp['repost_string'] = j.repost_string
            rp['user_sname'] = j.user_sname
            rp['user_url'] = j.user_url
            rp['content'] = j.content
            if hasattr(j,"from_user_sname"): 
                rp['from_user_sname'] = j.from_user_sname
                rp['from_user_url'] = j.from_user_url
            rp['time'] =  j.time.strftime("%Y%m%d-%H%M")
            obj['repost_list'].append(rp)
        return obj
    def saveJSON(self,outpath):
        jstr = self.toJSON()
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        filename = "%s/%s.json" % (outpath,self.mid)
        with codecs.open(filename, mode = "w", encoding = 'utf-8') as f:
            json.dump(jstr, f)
        logger.info("saved %s to %s" % (filename, outpath))
class WeiboRepost(object):
    """一条微博回复。
    
    Attributes:
        content: 内容
        time: 时间
        from_user_url: 转发来源url
        user_sname: 转发用户昵称
        user_url:
        from_user_sname: 来源用户昵称
        repost_string：未处理的完整回复内容
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
    gsidstack = [
        "4uen2019197u7V6AisnfDljB3cJ",\
        "4uZb201913vpBZoYAzmzlljB51W"
    ] # gsid循环队列，移到配置文件
    def __init__(self, gsidstack):
        self.gsidstack = gsidstack
    def popGsid(self):
        oldgsid = self.gsid
        self.gsid = self.gsidstack.pop(0)
        self.gsidstack.append(self.gsid)
        logger.warning("gsid %s changed to %s", *(oldgsid, self.gsid))
    def url2Dom(self, url, args=""):
        url = "%s?%s" % (url, args)# args = "page=1"
        logger.info("url2Dom parsing: %s", url)
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        opener.addheaders.append(('Cookie','gsid_CTandWM=' + self.gsid))
        urllib2.install_opener(opener)
        request = urllib2.Request(url, headers = self.HEADERS)
        response = urllib2.urlopen(request)
        data = response.read()
        dom = soupparser.fromstring(data)
        response.close()
        return dom
    def parseTime(self, time_string):
        time_string_split = time_string.split()
        # logger.info(time_string)
        # print "time_string: %s" % time_string
        match_ymd = re.compile(ur'(\d{4})-(\d{2})-(\d{2})').match(time_string_split[0])
        if len(time_string_split) == 1:
            # print "case1: xx ago"
            minutes = re.compile(ur'(.*)\u5206.*').match(time_string_split[0]).group(1) # 取得转发距现在过去了几分钟
            time = datetime.datetime.today()\
                +datetime.timedelta(minutes = 0-int(minutes)) # 时间赋值
        elif u'今天' in time_string_split:
            # print "case2: today xxx"
            time = time_string_split[1] # 取得转发时间HH:mm
            hour,minutes = time.split(":")
            today = datetime.date.today()
            time = datetime.datetime(today.year,\
                today.month,\
                today.day,\
                int(hour),int(minutes))
        elif u'月' in time_string_split[0] and u'\u65e5' in time_string_split[0]:
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
    def getTotalPage(self, url):
        dom = self.url2Dom(url)
        page_string = dom.xpath("//*[@id='pagelist']/form/div/text()")[-1]
        # 注意，此处并未考虑转发不足一页的情况
        page_number = int(re.compile(r".*\d+/(\d+)").match(page_string).group(1)) # 匹配页码并转成int型
        return page_number
class UserParser(Parser):
    """
        
    Attributes:
        user_url: 用户链接
        uid: 用户id
        nickname: 用户昵称
    """
    def __init__(self, gsidstack, user_url):
        Parser.__init__(self, gsidstack)
        self.popGsid()
        self.user_url = user_url
    def getUser(self):
        user = User()
        dom = self.url2Dom(self.user_url)
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
    def get_weibolist(self, page_limit):
        weibolist = []
        url = self.user_url
        j = 1
        while j < page_limit+1:
            try:
                self.get_weibo(j, weibolist)
            except Exception, e:
                logger.error("Exception: %s", e, exc_info=True)
                self.popGsid()
            else:
                j += 1
                tm.sleep(5)
        return weibolist

    def get_weibo(self, j, weibolist):
        logger.info("get weibo on page: %s", j)
        args = "page=%d" % j # 不设filter
        dom = self.url2Dom(self.user_url, args)
        divs = dom.xpath("//div[@class='c']")
        l = []
        # return dom
        if j == 1:
            nickname = dom.xpath("//div[@class='ut']/span[@class='ctt']")[0].text.split("[")[0]
            uid = dom.xpath(u"//div[@class='ut']/a[text()='资料']")[0].get('href').lstrip("/").rstrip("/info")
            self.nickname = nickname
            self.uid = uid
        else:
            nickname = self.nickname 
            uid = self.uid
        for i in divs:
            if not "id" in i.attrib.keys():
                continue # 标签没有id这一属性则跳过
            else:
                mid = i.attrib["id"].lstrip("M_") # 字符
                # logger.info("get mid: %s" % mid)
                id = sb.url_to_mid(mid) # 转为数字形式的mid
                # 取得 内容 时间 评论数 转发数 发布来源等
                content = "".join(i.xpath(".//span[@class='ctt']//text()")) # 只有微博内容
                str_line = "".join(i.xpath(".//text()")).replace(u'\xa0','') # 取得整个字符串后用正则匹配
                g = re.compile(ur".*转发理由:(.*)赞\[").match(str_line)
                if not g is None:
                    content = u"%s//转发微博:%s" % (g.group(1).strip(),content) # 前面加上转发理由
                g = re.compile(ur".*转发\[(\d*)\]评论\[(\d*)\].*来自(.*)").match(str_line) # match不到会出错
                repost_count = g.group(1) # 转发数
                comment_count = g.group(2) # 评论数
                from_str = g.group(3) # 来源
                time_str = i.xpath(".//span[@class='ct']")[0].text.split(u"来")[0]
                # logger.info(time_str)
                time = self.parseTime(time_str)
                timestamp = calendar.timegm(time.timetuple()) # 取得1970至今时间
                weibo = {}
                weibo["id"] = id
                weibo["name"] = uid
                weibo["nick"] = nickname
                weibo["repost"] = repost_count
                weibo["comment"] = comment_count
                weibo["from"] = from_str.replace(" ","")
                weibo["timestamp"] = timestamp
                weibo["content"] = content
                l.append(weibo)
        weibolist.extend(l)
        
    
    def get_midlist(self, page_limit):
        midlist = []# 如果要去重，应该用Set结构
        url = self.user_url
        j = 1
        while j < page_limit+1:
            try:
                self.get_mid(j, midlist)
            except Exception, e:
                logger.error("Exception: %s", e)
                self.popGsid()
            else:
                j += 1
            tm.sleep(5) # 为了避免错误，休眠
        return midlist
    def get_mid(self, j, midlist):
        logger.info("get mid on page: %s", j)
        args = "page=%d&filter=1" % j # 将filter设为1，抓取原创微博
        dom = self.url2Dom(self.user_url, args)
        divs = dom.xpath("//div[@class='c']")
        ori = []
        fin = []
        for i in range(0,len(divs)):
            ori.extend(divs[i].xpath("@id"))
        for i in ori:
            fin.append(i.lstrip("M_"))
        midlist.extend(fin)
    
class WeiboParser(Parser):
    """
    
    Attributes： 
        weibo_url: 链接
    """
    def __init__(self, gsidstack, weibo_url):
        Parser.__init__(self, gsidstack)
        self.popGsid()
        self.weibo_url = weibo_url
        logger.info("init WeiboParser for url: %s", weibo_url) 
    def getWeiboPost(self):
        """解析
        """
        weibopost = WeiboPost()
        url = self.weibo_url
        # 微博mid
        weibopost.mid =  re.compile(r"htt\S*\w+/(\S+)").match(url).group(1)
        flag = True
        while flag == True:
            dom = self.url2Dom(url)
            try:
                div = dom.xpath("//div[@id='M_']")[0] 
            except Exception, e:
                logger.error("Exception: %s", e)
                self.popGsid()
            else:
                flag = False
            
        user_url = "http://weibo.cn%s" % div.xpath("*/a")[0].get("href").split("?")[0]
        user_sname = div.xpath("*/a")[0].text
        weibopost.user_sname = user_sname # 微博发布者昵称
        #print "user_url: %s" % user_url
        #userparser = UserParser(user_url)
        #weibopost.user = userparser.getUser() # 微博发布者
        weibopost.user_url = user_url #微博发布者链接
        contentlist = div.xpath("*//span[@class='ctt']")[0].xpath(".//text()") # 微博内容抓取，此处需斟酌
        weibopost.content = "".join(contentlist) # 微博内容
        time_string =  div.xpath("*//span[@class='ct']")[0].text
        weibopost.post_time = self.parseTime(time_string) # 微博发布时间
        self._getReposts(self.weibo_url, weibopost.repost_list) 
        return weibopost
    def _getReposts(self, weibo_url, repost_list):
        """

        """
        lastpage = self.getTotalPage(weibo_url)
        i = lastpage
        j = 1
        while i != 0:
            logger.info("j: %d    i:%d", *(j, i))
            if j%400 == 0:
                self.popGsid()
            try:
                page_number, one_page = self._parseRepost(weibo_url, i)
            except Exception, e:
                logger.error("Exception: %s", e)
                self.popGsid()
            else:
                repost_list.extend(one_page)
                i = page_number - j
                j += 1
   
    def _parseRepost(self, url, page):
        reposts = []
        argstr = "page=%d" % page
        dom = self.url2Dom(url, argstr)
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
            a_line = "".join(divs[i].xpath(".//text()"))
            weibo_repost = WeiboRepost()
            weibo_repost.repost_string = a_line
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
    f = open("config.yaml")
    yamlconfig  = yaml.load(f) # 配置文件
    f.close()
    timeout = 20
    socket.setdefaulttimeout(timeout)
    #通过文件中的mid抓取微博
    midlistpath = yamlconfig["input"]["midlist"]
    outpath = yamlconfig["output"]["weibodir"]
    gsidstack = yamlconfig["input"]["gsidstack"]
    f = open(midlistpath,"r")
    midlist = []
    contents = f.readlines()
    for i in contents:
        midlist.append(i.rstrip("\n"))
    f.close()
    
    for j in midlist:
        filelist = os.listdir(outpath)
        processed = [i[0:-5] for i in filelist]
        if j in processed:
            logger.info("passed %s" , j)
            continue
        wp = WeiboParser(gsidstack, "http://weibo.cn/repost/%s" % j)
        try:
            total_page=wp.getTotalPage(wp.weibo_url)
            if total_page > 3000:
                continue # 由于抓取能力有限，暂时不处理3000页以上转评的微博
                logger.warning("passed %s for too many pages", j)
            weibopost = wp.getWeiboPost()
        except Exception, e:
            logger.error("Exception: %s", e)
            logger.warning("passed %s" , j)
            continue
        else:
            weibopost.saveJSON(outpath)
    



    """
    # 通过文件中的用户url抓取mid
    f = open("prepare/100users_meiti.txt")
    all_text = f.readlines()
    f.close()
    midlist = []
    for j in all_text:
        url = j.strip().split(",")[1]
        logger.info("User url: %s", url)
        up = UserParser(url)
        midlist.extend(up.get_midlist(10)) # 取了10页
    outfile = open("midlist","w")
    for i in midlist:
        outfile.write("%s\n" % i)
    outfile.close()
    """
    
    
    """
    up = UserParser("http://weibo.cn/cctvcaijing")
    midlist = up.get_midlist(10)
    """
    
    """
    midlist = [
                #"xjjQaekFq",\
                #"yA8UkBdsO",\
                #"z0N8Eh6B6",\
                #"A0IkRDiRp",\
                #"Ab3932Gsn",\
                #"Ab3XMydHq",\
                #"Ab5wf0Rsg",\
                #"AbbigE2Wa",\
                #"AbcexCVM8",\
                #"AbmW7jWQq",\
                #"AbuDAz8yp",\
                #"Abx5Hdtqa",\
                #"Abz7Ikpc8",\
                #"AbE5eDPco",\
                #"AbF3R1eDF",\
                #"Ac5wo6LJ2",\
                #"Ac6tV74nm",\
                #"Adb6ydQsN",\
                #"Adg2lyipu",\
                #"Adwwab87J",\
                #"AdGJfAcsn",\
                #"AdfMZv61a",\
                #"AdyvzEc60",\
                #"AdMAWhYLs",\
                #"AdAce72kt",\
                #"AdpXow9pj",\
                #"AhrkcwiJj"
                #]
    global text_list
    text_list = []
    for j in midlist:
        wp = WeiboParser("http://weibo.cn/repost/%s" % j)
        weibopost = wp.getWeiboPost()
        weibopost.saveJSON()
    """
    # wp = WeiboParser("http://weibo.cn/repost/AerZ9BKXm")
    # global text_list
    # text_list = []
    # weibopost = wp.getWeiboPost()
    # weibopost.saveJSON()
