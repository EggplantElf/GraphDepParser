

class Token:
    __slots__ = ['tid', 'form', 'lemma', 'pos', 'mor', 'head', 'label', 'ctag', 'chunkhead']

    def __init__(self, line, train = False):
        entries = line.split('\t')
        self.tid = int(entries[0])
        self.form = entries[1]
        self.lemma = entries[2]
        self.pos = entries[3]
        self.mor = entries[5]
        self.chunkhead = 0
        if train:
            self.head = int(entries[6])
            self.label = entries[7]
        else:
            self.head = 0
            self.label = ''
        
        # only NP
        if len(entries) > 10:
            self.ctag = entries[10].split('-')[0]

            # chunk = entries[10].split('-')
            # if chunk != ['O'] and chunk[1] == 'NP':
            #     self.ctag = chunk[0]
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

class Sentence(list):
    def __init__(self):
        self.append(Root())

    def add_token(self, token):
        self.append(token)

    def add_heads(self, arcs):
        for (h, d) in arcs:
            self[d].head = h

    def add_chunkheads(self, arcs):
        for (h, d) in arcs:
            self[d].chunkhead = h

    def to_str(self):
        return '\n'.join(t.to_str() for t in self[1:]) + '\n'


def read_sentence(filestream, train = False):
    print 'reading sentences ...'
    sentence = Sentence()
    # sentence.append(Root())
    i = 1
    for line in filestream:
        line = line.rstrip()
        if line:
            sentence.add_token(Token(line, train))
        elif len(sentence) != 1:
            yield sentence
            sentence = Sentence()
            i += 1
            if i % 100 == 0:
                print i

