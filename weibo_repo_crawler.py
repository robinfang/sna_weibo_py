#coding=utf-8
"""用于微博本身以及其转发详情的抓取。

"""
import urllib2
from lxml import etree
from StringIO import StringIO
import lxml.html.soupparser as soupparser
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
		user_url: 字符串用户链接
		content: 用户转发内容
		repost_time: 用户转发时间
	"""
	def __init__(self, user_url=None, content=None, repost_time=None):
		self.user_url = user_url
		self.content = content
		self.repost_time = repost_time
mid = "zAjoQmY0n"
gsid = "4uRR91f31V8gG7xcmM9k3703C8g"
url = "http://weibo.cn/repost/"
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20100101 Firefox/21.0"}
request = urllib2.Request("%s%s?&gsid=%s"%(url,mid,gsid),headers=headers)
data = urllib2.urlopen(request).read()
f = open('repo.xml','w')
f.write(data)
f.close()
#parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
#tree = etree.parse(StringIO(data),parser)
#divs = tree.xpath("//*[@class='c']")
#for j in divs:
#	for i in j.xpath('./*/text()'):
#		print i
#demo = divs[2].xpath('node()')
dom = soupparser.fromstring(data)
divs = dom.xpath("//*[@class='c']")
#weibo_post = WeiboPost()
#weibo_post.repost_list = []
for i in range(2,len(divs)):
    weibo_reply = WeiboReply()
    nodes  =  divs[i].xpath('node()')
    weibo_reply.user_url = "weibo.cn%s" % nodes[0].get('href')
    print weibo_reply.user_url
    time_string = nodes[-1].text
    print time_string
