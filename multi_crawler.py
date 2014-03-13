from weibo_crawler import *
import os
import fnmatch
path = "./prepare"
if __name__ == "__main__":
    timeout = 20
    socket.setdefaulttimeout(timeout)
    filelist = []
    files = os.listdir(path)
    for name in files:
        if fnmatch.fmatch(name, "*.txt"):
            filelist.append(os.path.join(path, name))
    