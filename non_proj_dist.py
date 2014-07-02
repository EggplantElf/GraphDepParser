import sys

STAT = {0:0}
NEW_STAT = {}

def read_sentence(filestream, limit = 0):
    print 'reading sentences ...'
    sent = Sentence()
    sent.pending.append(0)
    i = 1
    for line in filestream:
        line = line.rstrip()
        if line:
            items = line.split('\t')
            h, d = int(items[6]), int(items[0])
            sent.pending.append(d)
            sent.arcs.append((h, d))
        elif sent.pending:
            yield sent
            sent = Sentence()
            sent.pending.append(0)
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

    def __dist(self, arc):
        return self.pending.index(max(arc)) - self.pending.index(min(arc)) - 1

    def non_proj_arc(self):
        head = dict((d, h) for (h, d) in self.arcs)
        nps = []
        for (h, d) in self.arcs:
            for i in self.pending:
                if i > min(h, d) and i < max(h, d):
                    while i != 0 and i != h:
                        i = head[i]
                    if i == 0: # non-proj
                        if not any(i for (i, j) in self.arcs if i == d):
                            # return (h, d)
                            nps.append((h, d))
        if nps:
            return min(nps, key = self.__dist)
        return None


    def analyse(self):
        global STAT
        while len(self.pending) > 1:
            arc = self.allowed()
            if arc:
                self.update(arc)
                STAT[0] += 1
            else:
                np = self.non_proj_arc()
                assert np
                dist = len([i for i in self.pending if i > min(np) and i < max(np)])
                if dist not in STAT:
                    STAT[dist] = 0
                STAT[dist] += 1
                self.update(np)
                # break
                # l = len(self.pending)
                # if l not in NEW_STAT:
                #     NEW_STAT[l] = 1
                # else:
                #     NEW_STAT[l] += 1
                # break

def main(conll_file):
    for sent in read_sentence(open(conll_file)):
        sent.analyse()


if __name__ == '__main__':
    main(sys.argv[1])
    print STAT
    print NEW_STAT
