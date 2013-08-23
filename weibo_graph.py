#coding = utf-8
import networkx as nx
import codecs
def rl2Graph(rl):
    g = nx.DiGraph()
    for j in rl:
        if hasattr(j, "from_user_sname"):
            g.add_edge(j.from_user_sname, j.user_sname, {"content" : j.content})
        else:
            g.add_edge("origin", j.user_sname, {"content" : j.content})
    return g
def writeDotOutput(g, out):
    dot = ['"%s" -> "%s" [content="%s"]' % (n1, n2, g[n1][n2]['content'])\
            for (n1, n2) in g.edges()]
    f = codecs.open(out, 'w', encoding = 'utf-8')
    f.write('strict digraph {\n%s\n}' % ';\n'.join(dot))
    f.close()
        
