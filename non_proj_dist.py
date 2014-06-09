import sys
from copy import deepcopy

STAT = {}

def read_sentence(filestream, limit = 0):
    print 'reading sentences ...'
    sent = Sentence()
    i = 1
    for line in filestream:
        line = line.rstrip()
        if line:
            items = line.split('\t')
            h, d = int(items[6]), int(items[0])
            # if h != 0:
            sent.pending.append(d)
            sent.arcs.append((h, d))
        elif sent.pending:
            yield sent
            sent = Sentence()
            i += 1
            if limit and i == limit:
                break

class Sentence:
    def __init__(self):
        self.pending = []
        self.arcs = []

    def update(self, (h, d)):
        self.pending.remove(d)
        self.arcs.remove((h, d))

    def is_valid(self, h, d):
        return (h,d) in self.arcs and all(i != d for (i, j) in self.arcs)


    def allowed(self):
        for i in range(len(self.pending) - 1):
            p, q = self.pending[i], self.pending[i+1]
            if self.is_valid(p, q):
                return (p, q)
            if self.is_valid(q, p):
                return (q, p)


    def non_proj_arc(self):
        head = dict((d, h) for (h, d) in self.arcs)
        for (h, d) in self.arcs:
            for i in self.pending:
                if i > min(h, d) and i < max(h, d):
                    while i != 0 and i != h:
                        i = head[i]
                    if i == 0: # non-proj
                        if not any(i for (i, j) in self.arcs if i == d):
                            return (h, d)
        return None


    def analyse(self):
        global STAT
        while len(self.pending) > 1:
            arc = self.allowed()
            if arc:
                self.update(arc)
            else:
                np = self.non_proj_arc()
                # print self.pending
                # print self.arcs
                # print np
                # break
                assert np
                dist = len([i for i in self.pending if i > min(np) and i < max(np)])
                if dist not in STAT:
                    STAT[dist] = 0
                STAT[dist] += 1
                self.update(np)
                # break

def main(conll_file):
    for sent in read_sentence(open(conll_file)):
        sent.analyse()


if __name__ == '__main__':
    main(sys.argv[1])
    print STAT
