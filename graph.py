class Graph(dict):
    def __init__(self, score = {}):
        self.score = score
        for n in score:
            self[n] = score[n].keys()

    def add_nodes(self, nlist):
        for n in nlist:
            if n not in self:
                self[n] = []

    def remove_nodes(self, nlist):
        for n in nlist:
            self.pop(n, None)
            for d in self:
                if n in self[d]:
                    self[d].remove(n)

    def add_edges(self, elist):
        for (d, h) in elist:
            if d not in self:
                self[d] = []
            if h not in self[d]:
                self[d].append(h)

    def remove_edges(self, elist):
        for (d, h) in elist:
            if d in self and h in self[d]:
                self[d].remove(h)

    def subgraph(self, nlist):
        sub = Graph()
        sub.score = self.score
        for n in nlist:
            sub[n] = []
            for h in self[n]:
                if h in nlist:
                    sub[n].append(h)
