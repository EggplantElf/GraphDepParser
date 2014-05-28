from feature import make_features


class Token:
    def __init__(self, line):
        entries = line.split('\t')
        self.tid = int(entries[0])
        self.form = entries[1]
        self.lemma = entries[2]
        self.pos = entries[3]
        self.mor = entries[5]
        self.head = int(entries[6])
        self.label = entries[7]
        self.phead = '_'
        self.plabel = '_'

    def to_str(self):
        return '%d\t%s\t%s\t%s\t_\t%s\t%d\t%s\t%s\t%s' %\
            (self.tid, self.form, self.lemma, self.pos, self.mor, self.head, self.label, self.phead, self.plabel)

class Root(Token):
    def __init__(self):
        self.tid = 0
        self.form = 'ROOT'
        self.lemma = 'ROOT'
        self.pos = 'ROOT'
        self.mor = 'ROOT'

class Sentence(dict):
    def __init__(self):
        self[0] = Root()

    def add_token(self, token):
        self[len(self)] = token

    def add_heads(self, g):
        for (h, d) in g.edges():
            self[d].phead = h

    def to_str(self):
        return '\n'.join([self[i].to_str() for i in range(1, len(self))]) + '\n'



def read_sentence(filestream, limit = 100):
    print 'reading sentences ...'
    sentence = Sentence()
    i = 1
    for line in filestream:
        line = line.rstrip()
        if line:
            sentence.add_token(Token(line))
        elif len(sentence) != 1:
            yield sentence
            sentence = Sentence()
            i += 1
            if limit and i == limit:
                break

