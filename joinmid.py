#coding=utf-8
import os
import sys
import codecs
reload(sys)
sys.setdefaultencoding("utf-8")
def getFileList(path):
    filelist = []
    files = os.listdir(path)
    for name in files:
        filelist.append(os.path.join(path, name))
    return filelist
def getMidList(filepath):
    f = open(filepath)
    result = f.read().splitlines()
    f.close()
    return result
if __name__ == "__main__":
    filelist = getFileList(sys.argv[1])
    midlist = []
    for j in filelist:
        midlist.extend(getMidList(j))
    with codecs.open(sys.argv[2], mode = "w", encoding = 'utf-8') as f:
        f.write("\n".join(list(set(midlist)))+"\n")    