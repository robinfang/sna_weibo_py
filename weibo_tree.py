#coding=utf-8
import uuid
import pdb
import json
def text2List(all_text):
    """将文本转换成三元组组成的list
    """
    all_list = []
    for line in all_text:
        l = line.split()
        name = l[0].strip().strip('"')
        to_name = l[2].strip().strip('"')
        content = l[3].strip().strip('"').lstrip('[content="').rstrip('//"];')
        all_list.append((name, to_name, content))
    return all_list
def list2Dict(all_list):
    """将三元组list转换成字典的字典，待建立关系节点
    """
    all_dict = {}
    for i in all_list:
        name = i[0]
        node = {}
        node["id"] = str(uuid.uuid4())
        node["name"] = i[0]
        node["data"] = {"content":i[2]}
        node["children"] = []
        all_dict[name] = node
    for j in all_list:
        name = j[1]
        node = {}
        node["id"] = str(uuid.uuid4())
        node["name"] = j[1]
        node["data"] = {"content":j[2]}
        node["children"] = []
        all_dict[name] = node
    return all_dict    
def list2Rel(all_list):
    """从三元组list中抽取关系
    """
    all_rel = {}
    for j in all_list:
        if j[0] in all_rel.keys():
            all_rel[j[0]].append(j[1])
        else:
            all_rel[j[0]] = [j[1]]
    return all_rel
def findSub(name, all_rel):
    if name in all_rel.keys():
        # subnodes = all_rel[name]
        subnodes = all_rel.pop(name)
        return subnodes
    else:
        return []
def genTree(name, all_dict, all_rel):
    # pdb.set_trace()
    tree = {}
    tree = all_dict[name]
    subnodes = findSub(tree["name"], all_rel) 
    while len(subnodes) > 0:
        snode = subnodes.pop()
        tree["children"].append(genTree(snode, all_dict, all_rel))
    return tree

def findCircular(tree, visited):
    children = tree["children"]
    while len(children) > 0:
        snode = children.pop()
        if not snode["name"] in visited:
            visited.append(snode["name"])
            findCircular(snode,visited)
        else:
            print "back edge: %s -> %s" % (tree["name"], snode["name"]) 
if __name__ == "__main__":
    f = open("right.txt", "r")
    all_text = f.readlines()
    f.close()
    all_list = text2List(all_text) # 文本变成三元组组成的list，作为两次扫描的对象
    all_dict = list2Dict(all_list) # 获取所有节点的字典，尚未建立关系
    # global all_rel
    all_rel = list2Rel(all_list) # 获取关系字典
    print (len(all_rel))
    tree = genTree("origin", all_dict, all_rel)
    print (len(all_rel))
    visited = []
    findCircular(tree, visited)
    f = open("json","w")
    json_str = json.dumps(tree)
    f.write(json_str)
    f.close()
