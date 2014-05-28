import networkx as nx

def MST(score):
    g = nx.DiGraph(score.keys())
    go = CLE(g, score, 0)
    go.remove_nodes_from([n for n in go.nodes() if n < 0])
    return go

def CLE(g, s, tc):
    # print 'CLE'
    a = [max(g.in_edges(d), key = lambda x: s[x]) for d in g if d != 0]
    ga = nx.DiGraph(a)
    ga.add_nodes_from(g)
    cycles = list(nx.simple_cycles(ga))
    if not cycles:
        return ga
    else:
        c = ga.subgraph(cycles[0])
        gc, tc = contract(g, c, s, tc)
        y = CLE(gc, s, tc)
        return resolve(y, c, s)



# change sum([]) to sum()
def contract(g, c, s, tc):
    # print 'contract'
    g.remove_nodes_from(c)
    vo = g.nodes()
    vi = g.nodes()
    if 0 in vo:
       vo.remove(0)
    tc -= 1
    sc = sum([s[e][0] for e in c.edges()])
    g.add_node(tc)
    for td in vo:
        th = max(c, key = lambda x: s[(x, td)][0])
        g.add_edge(tc,td)
        s[(tc, td)] = (s[(th, td)][0], [(th, td)])

    for th in vi:
        td = max(c, key = lambda x: s[(th, x)][0] + sc - s[c.in_edges(x)[0]][0])
        g.add_edge(th, tc)
        edges = [(h,d) for (h,d) in c.edges() if d != td] + [(th, td)]
        s[(th, tc)] = (s[(th, td)][0] + sc - s[c.in_edges(td)[0]][0], edges)

    return g, tc


def resolve(g, c, s):
    # print 'resolve'
    for e in g.edges():
        if e not in s[e][1]:
            g.remove_edges_from([e])
            g.add_edges_from(s[e][1])
    return g

def plot(g, s):
    nx.write_dot(g, 'grid.dot')    
    ga=pgv.AGraph("grid.dot")
    ga.layout(prog='dot')
    ga.draw('result.png')
    os.system('open result.png')
    for k in s:
        if k in g.edges():
            print k, s[k]
    raw_input()