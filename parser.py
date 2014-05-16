import os, codecs, cPickle, gzip, time
import networkx as nx
import matplotlib.pyplot as plt
import pygraphviz as pgv

flag = 0

####################################################
# classes

class Token:
    def __init__(self, line):
        entries = line.split('\t')
        self.tid = int(entries[0])
        self.form = entries[1]
        self.lemma = entries[2]
        self.pos = entries[3]
        self.head = int(entries[6])
        self.label = entries[7]
        self.phead = -1

    def to_str(self):
        return '%d\t%s\t%s\t%s\t_\t_\t%d\t%s\t%s\t_' %\
            (self.tid, self.form, self.lemma, self.pos, self.head, self.label, self.phead)

class Root(Token):
    def __init__(self):
        self.tid = 0
        self.form = 'ROOT'
        self.lemma = 'ROOT'
        self.pos = 'ROOT'

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

    def get_scores(self, model, vectors):
        score = {}
        for d in vectors:
            for h in vectors[d]:
                score[(h,d)] = (model.score(vectors[d][h]), [(h,d)])
        return score

    def get_vectors(self, map_func):
        vectors = {}
        for d in range(1, len(self)):
            vectors[d] = {}
            for h in range(0, len(self)):
                if h != d:
                    vectors[d][h] = make_features(self, h, d, map_func)
        return vectors


class Model:
    def __init__(self, modelfile = None):
        self.featmap = {}
        if modelfile:
            self.load(modelfile)

    def make_weights(self):
        self.weights = [0.0 for f in xrange(self.numfeatures())]


    def save(self, modelfile):
        stream = open(modelfile,'wb')
        cPickle.dump(self.weights,stream,-1)
        cPickle.dump(self.featmap,stream,-1)
        stream.close()

    def load(self, modelfile):
        stream = open(modelfile,'rb')
        self.weights = cPickle.load(stream)
        self.featmap = cPickle.load(stream)
        stream.close()

    def numfeatures(self):
        return len(self.featmap)

    def register_feature(self, feature):
        if feature not in self.featmap:
            self.featmap[feature] = self.numfeatures()+1
            return self.numfeatures()
        return self.featmap[feature]

    def map_feature(self, feature):
        return self.featmap.get(feature,None)

    def score(self, vector):
        # print vector
        # print len(self.weights)
        return sum(map(lambda x: self.weights[x - 1], vector))
        # return sum(map(mul, vector, self.weights))

    def predict(self, vectors):
        # print vectors
        return max(vectors, key = lambda h: self.score(vectors[h]))

    def update(self, gold_feat, pred_feat):
        # print gold_feat, pred_feat
        # print self.weights
        for i in gold_feat:
            # print self.weights[i-1],
            self.weights[i-1] += 1
            # print self.weights[i-1]
        for i in pred_feat:
            self.weights[i-1] -= 1
        # print self.weights
####################################################


####################################################
# IO

def read_sentence(filestream):
    print 'reading sentences'
    sentence = Sentence()
    for line in filestream:
        line = line.rstrip()
        if line:
            sentence.add_token(Token(line))
        elif len(sentence) != 1:
            yield sentence
            sentence = Sentence()
    print 'done'

# change!!!
def write_to_file( label, features, fileobj ):
    features = set(features)
    # features.discard(None)
    print >> fileobj, '%d %s' % (label,' '.join(map(lambda x: '%d:1' % x,sorted(features))))


####################################################



####################################################
# ML
def make_features(sent, h, d, map_func):
    features = []
    # features.append(map_func('head.pos:%s' % sent[h].pos))
    # features.append(map_func('head.form:%s' % sent[h].form))
    features.append(map_func('head.pos+dep.pos:%s+%s' % (sent[h].pos, sent[d].pos)))
    features.append(map_func('head.pos+dep.form:%s+%s' % (sent[h].pos, sent[d].form)))
    features.append(map_func('head.form+dep.pos:%s+%s' % (sent[h].form, sent[d].pos)))

    features.append(map_func('offset:%d' % (h - d)))
    features.append(map_func('between.pos:%s' % '+'.join(map(lambda x: sent[x].pos, range(h+1, d)))))

    return filter(lambda x: x, features)


def train(conll_file, model_file, epochs = 10):
    instances = []
    model = Model()
    i = 0
    for sent in read_sentence(open(conll_file)):
        i += 1
        if i % 100 == 0:
            print '.',
        edge_vectors = sent.get_vectors(model.register_feature)
        for d in edge_vectors:
            h = sent[d].head # not -1
            instances.append((h, edge_vectors[d]))
    model.make_weights()

    print 'start training ...'
    for epoch in xrange(epochs):
        correct = 0
        total = 0      
        i = 0
        for (gold, head_vectors) in instances:
            pred = model.predict(head_vectors)
            if gold != pred:
                model.update(head_vectors[gold], head_vectors[pred])
            else:
                correct += 1
            total += 1
            # print correct, total
            i += 1
            if i % 1000 == 0:
                print '.',
        print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)
        print sum(model.weights)
        # print model.weights
    model.save(model_file)


# use MST in training instead of gready finding head
def train_MST():
    pass


def test(conll_file, model_file, output_file):
    outstream = open(output_file,'w')
    model = Model(model_file)
    for sent in read_sentence(open(conll_file)):
        edge_vectors = sent.get_vectors(model.map_feature)
        score = sent.get_scores(model, edge_vectors)
        graph = MST(score)
        sent.add_heads(graph)
        print >> outstream, sent.to_str()

    outstream.close()
####################################################







####################################################
# Chu-Liu-Edmond Algorithm

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
    if flag:
        plot(ga, s)
    cycles = list(nx.simple_cycles(ga))
    if not cycles:
        return ga
    else:
        c = ga.subgraph(cycles[0])
        gc, tc = contract(g, c, s, tc)
        y = CLE(gc, s, tc)
        return resolve(y, c, s)

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
    if flag:
        plot(g, s)
    return g

####################################################



####################################################
# helpers

# def show(g):
#     print g.nodes()
#     print g.

def plot(g, s):
    # if mapping:
    #     g = nx.relabel_nodes(g,mapping)
    nx.write_dot(g, 'grid.dot')    
    ga=pgv.AGraph("grid.dot")
    ga.layout(prog='dot')
    ga.draw('result.png')
    os.system('open result.png')
    for k in s:
        if k in g.edges():
            print k, s[k]
    raw_input()

def evaluate(conll_file):
    total = 0.0
    correct = 0.0
    for line in open(conll_file):
        if line.strip():
            items = line.split('\t')
            total += 1
            if items[6] == items[8]:
                correct += 1
    print 'accuracy: %6.2f%%' % (100 * correct/total)

def debug(conll_file, model_file):
    model = Model(model_file)   
    for sent in read_sentence(open(conll_file)):
        edge_vectors = sent.get_vectors(model.map_feature)
        score = sent.get_scores(model, edge_vectors)
        graph = MST(score)
        sent.add_heads(graph)
        print sent.to_str()



####################################################

if __name__ == '__main__':
    t0 = time.time()
    train('../data/english/train/wsj_train.first-5k.conll06', 'tmp.model')
    test('../data/english/dev/wsj_dev.conll06', 'tmp.model', 'out.conll06')
    evaluate('out.conll06')
    # debug('debug.conll06', 'tmp.model')
    print time.time() - t0