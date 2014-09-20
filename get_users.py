#coding=utf-8
import json
import os
import codecs
def getUserUrlList(filepath):
    urlList = []
    f = open(filepath)
    aStr = f.read()
    f.close()
    aPost = json.loads(aStr)
    urlList.append(aPost["user_url"])
    commentList = aPost["repost_list"]
    for i in commentList:
        urlList.append(i["user_url"])
        if i.has_key("from_user_sname"):
            urlList.append(i["from_user_sname"])
    return list(set(urlList))
    
def getUrlFromDir(path):
    files = os.listdir(path)
    urlList = []
    filelist = []
    for name in files:
       filelist.append(os.path.join(path, name))
    for i in filelist:
        urlList.extend(getUserUrlList(i))
    return list(set(urlList))

if __name__ == "__main__":
    urlList = getUrlFromDir("F:/forpond/outpath")
    f =  codecs.open("user_url_list.txt", mode = "w", encoding = 'utf-8')
    f.write("\n".join(urlList)+"\n")
