

class Token:
    __slots__ = ['tid', 'form', 'lemma', 'pos', 'mor', 'head', 'label']

    def __init__(self, line):
        entries = line.split('\t')
        self.tid = int(entries[0])
        self.form = entries[1]
        self.lemma = entries[2]
        self.pos = entries[3]
        self.mor = entries[5]
        self.head = entries[6]
        if self.head != '_':
            self.head = int(self.head)
        self.label = entries[7]

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

    def to_str(self):
        return '\n'.join(t.to_str() for t in self[1:]) + '\n'


def read_sentence(filestream, limit = None):
    print 'reading sentences ...'
    sentence = Sentence()
    # sentence.append(Root())
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
            if i % 100 == 0:
                print i

