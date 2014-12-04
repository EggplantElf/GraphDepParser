

class Token:
    __slots__ = ['tid', 'form', 'lemma', 'pos', 'mor', 'head', 'label', 'cnum', 'ctag', 'unithead', 'boc', 'eoc']

    def __init__(self, line, train = False):
        entries = line.split('\t')
        self.tid = int(entries[0])
        self.cnum = self.tid
        self.form = entries[1]
        self.lemma = entries[2]
        self.pos = entries[3]
        self.mor = entries[5]
        self.unithead = 0
        self.boc = -1
        self.eoc = -1
        if train:
            self.head = int(entries[6])
            self.label = entries[7]
        else:
            self.head = 0
            self.label = ''
        
        # only NP
        if len(entries) > 10:
            self.ctag = entries[10]
            # self.ctag = entries[10].split('-')[0]

            # unit = entries[10].split('-')
            # if unit != ['O'] and unit[1] == 'NP':
            #     self.ctag = unit[0]
            # else:
            #     self.ctag = 'O'




    def to_str(self):
        return '%d\t%s\t%s\t%s\t_\t%s\t%d\t%s\t_\t_' %\
            (self.tid, self.form, self.lemma, self.pos, self.mor, self.head, self.label)


class Root(Token):
    def __init__(self):
        self.tid = 0
        self.form = 'ROOT'
        self.lemma = 'ROOT'
        self.pos = 'ROOT'
        self.mor = 'ROOT'
        self.unithead = 0
        self.ctag = 'ROOT'
        self.boc = -2
        self.eoc = -2
        self.cnum = -2

class Sentence(list):
    def __init__(self):
        self.append(Root())

    def add_token(self, token):
        self.append(token)

    def add_heads(self, arcs):
        for (h, d) in arcs:
            self[d].head = h

    def add_unitheads(self, arcs):
        for (h, d) in arcs:
            self[d].unithead = h

    def to_str(self):
        return '\n'.join(t.to_str() for t in self[1:]) + '\n'


def read_sentence(filestream, train = False):
    print 'reading sentences ...'
    sentence = Sentence()
    i = 1
    for line in filestream:
        line = line.rstrip()
        if line:
            sentence.add_token(Token(line, train))
        elif len(sentence) != 1:
            add_eoc_tags(sentence)
            yield sentence
            sentence = Sentence()
            i += 1
            if i % 100 == 0:
                print i


def add_eoc_tags(sent):
    chunk = []
    for t in range(1, len(sent)):
        if sent[t].ctag[0] in ['B', 'O']:
            for i in range(len(chunk)):
                sent[chunk[i]].boc = i
                sent[chunk[i]].eoc = len(chunk) - i
                sent[chunk[i]].cnum = sent[chunk[0]].cnum
            if sent[t].ctag[0] == 'B':
                chunk = [t]
            else:
                chunk = []
        elif sent[t].ctag[0] == 'I':
            chunk.append(t)

    for i in range(len(chunk)):
        sent[chunk[i]].boc = i
        sent[chunk[i]].eoc = len(chunk) - i
        sent[chunk[i]].cnum = sent[chunk[0]].cnum


