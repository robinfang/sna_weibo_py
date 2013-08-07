#coding=utf-8
class User(object):
    """微博用户
    Attributes:
        url: 
        mid: 
        following_number: 
        follower number: 
        sex: 
        age: 
        tags: 
    """
class WeiboPost(object):
    """一条新浪微博。
    Attributes:
        mid: 字符串，微博的mid，形如zAjoQmY0n
        user: 字符串发布者
        post_time: 发布时间
        content: 字符串内容
        repost_list: WeiboReply回复列表
    """
    def __init__(self, mid=None, user=None, post_time=None, content=None):
        self.mid = mid
        self.user = user
        self.post_time = post_time
        self.content = content

