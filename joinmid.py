#coding=utf-8
import os
import sys

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
    f = open(sys.argv[2],"w")
    f.write("\n".join(midlist))
    f.close()