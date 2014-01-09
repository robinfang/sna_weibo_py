from weibo_crawler import *

class AnyParser(Parser):
    def __init__(self, url):
        self.popGsid()
        self.url = url
    def getUsers(self):
        user_list = []
        total_page = self._getTotalPage(self.url)
        for j in range(1,total_page+1):
            logger.info("get user on page: %s", j)
            args = "cat=media&page=%d" % j
            dom = self.url2Dom(self.url, args)
            li = dom.xpath("//table//*/a[@class='nk']")
            for k in li:
                url = k.get("href").split("?")[0]
                user_list.append(url)
        return user_list    
if __name__ == "__main__":
    ap = AnyParser("http://weibo.cn/pub/top")
    li = ap.getUsers()
    full = []
    for i in li:
        up = UserParser(i)
        midlist = up.get_midlist(3)
        full.extend(midlist)
    print full    