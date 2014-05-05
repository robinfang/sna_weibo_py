#coding=utf-8
import urllib2
from lxml import etree
import re
import lxml.html.soupparser as soupparser
import datetime
import time
import json
import codecs
import os
import logging 
import socket



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
    def saveJSON(self):
        outpath = "../weibo_3_20_test"
        jstr = self.toJSON()
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        filename = "%s/%s.json" % (outpath,self.mid)
        
        with codecs.open(filename, mode = "w", encoding = 'utf-8') as f:
            json.dump(jstr, f)
        logger.info("saved: %s", filename)
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
        "gsid=4ubJ52971LNmaiYcOV5GdfNr36t",\
        "gsid=4urA52971PxaSOrKfzGuRfO7L2W",\
        "gsid=4upQ529713UHdNmh53B2WfOyUcU",\
        "gsid=4uJk201917rxYqNXKULdNfOzh70",\
        "gsid=4uzx20191xU2kBTWOeotKfRRm5x",\
        "gsid=4usQ20191yHvCSzEwVnM3fRRp2V",\
        "gsid=4uA520191mPCY88mbEmmnf8Qu01",\
        "gsid=4u2C20191euGoJQw9p6FhfV3b07",\
        "gsid=4uRs20191mfyMSu2dNVdpfV3h86",\
        "gsid=4u4r20191qXMqHb9E6IfDf9YVfh",\
        "gsid=4u3c20191bDoB10FrtvYmf8Qvec",\
        "gsid=4uAm20191UgnC3LyuITrhfUcM4S",\
        "gsid=4uu420191hHH0lpj07RfEfUcQdi",\
        "gsid=4uSL20191bI7zCqEIVw7tfUWs4g",\
        "gsid=4u7e20191pQ4b0Hl3Z1fblgRicr",\
        "gsid=4u0l20191gpNhTVGprQ26lgMeai",\
        "gsid=4ufA2019148bPad7zmem7lgRj9z",\
        "gsid=4uVZ20191vQdR7aYwmIIFlgMf3e",\
        "gsid=4uxt20191DAWNxc9NAwkNlgMf9d",\
        "gsid=4ujh20191edQb8jr6pdnMlgNo5b",\
        "gsid=4uLf20191qhBaN23MnlddlgHC9I",\
        "gsid=4uJR20191vFWifTk7Yii4lgHA0E",\
        "gsid=4ust20191rltkvQlr5GPWlgHB0x",\
        "gsid=4ubD20191LQzdHykR8E2NlgHD68",\
        "gsid=4urh20191EAYVKvxuHGeFljLV78",\
        "gsid=4ux62019197i6Gvn2BRRxljM1fi",\
        "gsid=4u8G20191S6yZvse2c4CxljYC19",\
        "gsid=4uen2019197u7V6AisnfDljB3cJ",\
        "gsid=4uZb201913vpBZoYAzmzlljB51W"
    ]
    def popGsid(self):
        oldgsid = self.gsid
        self.gsid = self.gsidstack.pop(0)
        self.gsidstack.append(self.gsid)
        logger.warning("gsid %s changed to %s", *(oldgsid, self.gsid))
    def url2Dom(self, url, args=""):
        
        url = "%s?%s&%s" % (url, self.gsid, args)# args = "page=1"
        logger.info("url2Dom parsing: %s", url)
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
        request = urllib2.Request(url, headers = self.HEADERS)
        response = urllib2.urlopen(request)
        data = response.read()
        dom = soupparser.fromstring(data)
        response.close()
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
    """
    def __init__(self, user_url):
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
            time.sleep(0.5) # 为了避免错误，休眠
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
    def __init__(self, weibo_url):
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

    timeout = 20
    socket.setdefaulttimeout(timeout)
    global outpath
    outpath = "../weibo_3_20_test"
    
    #通过文件中的mid抓取微博
    f = open("midlist","r")
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
        wp = WeiboParser("http://weibo.cn/repost/%s" % j)
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
            weibopost.saveJSON()
    



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
