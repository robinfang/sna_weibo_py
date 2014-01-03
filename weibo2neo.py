#coding=utf-8
import json
from py2neo import neo4j

def queryOneNode(label, key, value):
    query_str = "match (n:%s) where n.%s='%s' return (n)" % (label, key, value)
    
    graph_db = neo4j.GraphDatabaseService()
    query = neo4j.CypherQuery(graph_db, query_str)
    a, = query.execute()
    return a[0]
    
    
def buildRef(a, type, b):
    r = neo4j.Relationship.abstract(a, type, b)
    ref, = graph_db.create(r)
    return ref
if __name__ == "__main__":
    f = open("AbdZUAPuT.json","r")
    djson = json.loads(f.read())
    f.close()
    graph_db = neo4j.GraphDatabaseService()
    p, = graph_db.create({})
    p.add_labels("Post")
    p["mid"] = "AbdZUAPuT"
    p["name"] =  djson["user_sname"]
    p["content"] =  djson["content"]
    p["time"] = ""
    repost_list = djson["repost_list"]
    sorted_list = sorted(repost_list, key = lambda x: x["time"])
    treelist = [] #保存已经存好的节点
    tree = {}
    for j in sorted_list:
        if not j["user_sname"] in treelist:
            rp, = graph_db.create({})
            rp.add_labels("Repost")
            rp["time"] = j["time"]
            rp["name"] = j["user_sname"]
            rp["content"] = j["content"]
            #buildRef(p, "HAS", rp)
            tree[j["user_sname"]] = rp
            treelist.append(j["user_sname"])
            if j.has_key("from_user_sname"):
                if  j["from_user_sname"] in treelist:
                    #fromp = queryOneNode("Repost", "name", j["from_user_sname"])
                    fromp = tree[j["from_user_sname"]]
                    buildRef(fromp, "TO", rp)
                else:
                    print "can't find parent node :%s" % j["from_user_sname"]
                    buildRef(p, "TO", rp)
            else:
                buildRef(p, "TO", rp)
        else:
            print "%s already exist." % j["user_sname"]
    #循环外应释放tree和treelist等变量            