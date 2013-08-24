#coding = utf-8

def text2Dict(all_text):
    all_dict = {}
    for line in all_text:
        l = line.split()
        name = l[0].strip().strip('"')
        to_name = l[2].strip().strip('"')
        content = l[3].strip().strip('"').lstrip('[content="').rstrip('//"];')
        print "name: %s , to_name: %s, content: %s" %(name, to_name, content)
        if not name in all_dict.keys():
            node = {}
            node["name"] = name
            node["content"] = content
            node["children"] = []
            node["children"].append(to_name)
        else:
            node = all_dict[name]
            node["children"].append(to_name)
        all_dict[name] = node
    return all_dict
def dict2List(all_dict):
    all_list = []
    for k, v in all_dict.iteritems():
        all_list.append(v)
    return all_list
def findInList(name, all_list):
    for i in range(0, len(all_list)):
        if all_list[i]["name"] == name: 
            print i
            return all_list[i]
    return None
def genTree(name, all_list):
    tree = {}
    tree["name"] = name 
    node = findInList(name, all_list)
    if node != None:
        tree["content"] = node["content"]
        tree["children"] = []
        while len(node["children"]) > 0:
            n = node["children"].pop()
            tree["children"].append(genTree(n, all_list))
    return tree
if __name__ == "__main__":
    f = open("right.txt","r")
    all_text = f.readlines()
    f.close()
    all_dict = text2Dict(all_text)
    all_list = dict2List(all_dict)
    result = genTree("origin",all_list)
            

