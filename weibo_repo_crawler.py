#!/usr/bin/python
#coding=utf-8
import urllib2
from lxml import etree 
from StringIO import StringIO
import lxml.html.soupparser as soupparser
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

