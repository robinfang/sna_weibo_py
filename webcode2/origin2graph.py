#coding=utf-8
import json
import math
import codecs
import random
def buildRef(edge_list, fromnode, tonode, id):
    rel = {}
    rel["source"] = fromnode["id"]
    rel["target"] = tonode["id"]
    rel["id"] = "e%d" % id
    edge_list.append(rel)
    tonode["level"] = fromnode["level"] + 1
    """ 
    level = tonode["level"]
    xold = fromnode["x"]
    yold = fromnode["y"]
    old = math.atan(yold/(xold+0.000000000001))
    delta = 2*math.pi/math.pow(level,10)
    p = math.sqrt(level)
    #p = math.sqrt(xold*xold + yold*yold) + 100000/level/level 
    xnew = p*math.cos(old + random.uniform(-delta, delta))
    ynew = p*math.sin(old + random.uniform(-delta, delta))
    tonode["x"] = xnew
    tonode["y"] = ynew
    """
    a = math.pow(tonode["level"],5)
    tonode["x"] = fromnode["x"]+1000*tonode["level"]
    tonode["y"] = fromnode["y"]+random.uniform(-2000/a, 2000/a)
    
    
def origin2graph(path):
    f = open(path)
    ojson = json.loads(f.read())
    f.close()
    repost_list = ojson["repost_list"]
    sorted_list = sorted(repost_list, key = lambda x: x["time"])
    treelist = [] #保存已经存好的节点的用户名
    tree = {}
    
    gjson = {}
    gjson["nodes"] = []
    gjson["edges"] = []
    originnode = {}
    originnode["id"] = "n0"
    originnode["label"] = ojson["user_sname"]
    originnode["x"] = 0
    originnode["y"] = 0
    originnode["size"] = 4
    originnode["level"] = 0
    gjson["nodes"].append(originnode)
    id = 1
    for item in sorted_list:
        if not item["user_sname"] in treelist:
            node={}
            node["label"] = item["user_sname"]
            node["id"] = item["user_sname"]
            node["size"] = 1
            gjson["nodes"].append(node) # 向gjson中添加节点
            tree[node["label"]] = node
            treelist.append(node["label"])
            if item.has_key("from_user_sname"):
                if item["from_user_sname"] in treelist:
                    fromnode = tree[item["from_user_sname"]]
                    buildRef(gjson["edges"], fromnode, node, id) # 在gjson中建立关系 fromnode to node
                
                else:
                    print "can't find parent node :%s" % item["from_user_sname"]
                    buildRef(gjson["edges"], originnode, node, id) # 在gjson中建立关系 fromnode to node# 建立关系 originnode to node
            else:
                buildRef(gjson["edges"], originnode, node, id) # 在gjson中建立关系 originnode to npde
        else: 
            print "%s already exist." % item["user_sname"]
        id += 1
    return gjson
if __name__ == "__main__":
    gjson = origin2graph("AAbpCmPuz.json")
    with codecs.open("demo.json", mode = "w", encoding = 'utf-8') as f:
        json.dump(gjson, f)
    #print gjson