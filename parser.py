import sys, os, codecs, cPickle, gzip, math, time, random
import networkx as nx
# import matplotlib.pyplot as plt
# import pygraphviz as pgv

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
        self.mor = entries[5]
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
        self.weights = []
        self.delta = []
        if modelfile:
            self.load(modelfile)

    def make_weights(self):
        self.weights = [0.0 for f in xrange(self.numfeatures())]
        self.delta = [0.0 for f in xrange(self.numfeatures())]

    def save(self, modelfile):
        stream = gzip.open(modelfile,'wb')
        self.drop_zero_features()
        cPickle.dump(self.weights,stream,-1)
        cPickle.dump(self.featmap,stream,-1)
        stream.close()


    def drop_zero_features(self):
        new_weight = []
        new_featmap = {}
        q = 1
        for f in self.featmap:
            i = self.featmap[f]
            if math.fabs(self.weights[i-1]) > 0.001:
                new_weight.append(self.weights[i-1])
                new_featmap[f] = q
                q += 1
        self.featmap = new_featmap
        self.weights = new_weight


    def load(self, modelfile):
        stream = gzip.open(modelfile,'rb')
        self.weights = cPickle.load(stream)
        self.featmap = cPickle.load(stream)
        stream.close()

    def numfeatures(self):
        return len(self.featmap)

    def register_feature(self, feature):
        if feature not in self.featmap:
            self.featmap[feature] = self.numfeatures()+1
            self.weights.append(0.0)
            self.delta.append(0.0)
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

    def update(self, gold_feat, pred_feat, q = 1):
        # print gold_feat, pred_feat
        # print self.weights
        for i in gold_feat:
            # print self.weights[i-1],
            self.weights[i-1] += 1
            self.delta[i-1] += q
            # print self.weights[i-1]
        for i in pred_feat:
            self.weights[i-1] -= 1
            self.delta[i-1] -= q
        # print self.weights

    def average(self, q):
        # print self.weights[:30]
        # print self.delta[:30]
        for i in range(len(self.weights)):
            self.weights[i] -= self.delta[i] / q
        # print self.weights[:30]

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

    nodes = range(1, len(sent))
    hpos, hform, hmor = sent[h].pos, sent[h].form, sent[h].mor
    dpos, dform, dmor = sent[d].pos, sent[d].form, sent[d].mor
    h01pos = (h != 0 and h-1 in nodes) and sent[h-1].pos or '<NA>'
    h02pos = (h != 0 and h-2 in nodes) and sent[h-2].pos or '<NA>'
    h11pos = (h != 0 and h+1 in nodes) and sent[h+1].pos or '<NA>'
    h12pos = (h != 0 and h+2 in nodes) and sent[h+2].pos or '<NA>'


    d01pos = (d != 0 and d-1 in nodes) and sent[d-1].pos or '<NA>'
    d11pos = (d != 0 and d+1 in nodes) and sent[d+1].pos or '<NA>'
    d11pos = (d != 0 and d+1 in nodes) and sent[d+1].pos or '<NA>'
    d12pos = (d != 0 and d+2 in nodes) and sent[d+2].pos or '<NA>'


    if h < d:
        features.append(map_func('head.pos~dep.pos:%s~%s' % (hpos, dpos)))
        features.append(map_func('head.pos~dep.form:%s~%s' % (hpos, dform)))
        features.append(map_func('head.form~dep.pos:%s~%s' % (hform, dpos)))
        features.append(map_func('head.form~dep.form:%s~%s' % (hform, dform)))
        features.append(map_func('head.mor~dep.mor:%s~%s' % (hmor, dmor)))
        features.append(map_func('head.mor~head.pos~dep.mor~dep.pos:%s~%s~%s~%s' % (hmor, hpos, dmor, dpos)))

    else:
        features.append(map_func('dep.pos~head.pos:%s~%s' % (dpos, hpos)))
        features.append(map_func('dep.pos~head.form:%s~%s' % (dpos, hform)))
        features.append(map_func('dep.form~head.pos:%s~%s' % (dform, hpos)))
        features.append(map_func('dep.form~head.form:%s~%s' % (dform, hform)))
        features.append(map_func('dep.mor~head.mor:%s~%s' % (dmor, hmor)))
        features.append(map_func('dep.mor~dep.pos~head.mor~head.pos:%s~%s~%s~%s' % (dmor, dpos, hmor, hpos)))

    # features.append(map_func('head.pos~dep.form~dep.pos:%s~%s~%s' % (hpos, dform, dpos)))
    # features.append(map_func('head.form~dep.form~dep.pos:%s~%s~%s' % (hform, dform, dpos)))
    # features.append(map_func('head.form~head.pos~dep.pos:%s~%s~%s' % (hform, hpos, dpos)))
    # features.append(map_func('head.form~head.pos~dep.form:%s~%s~%s' % (hform, hpos, dform)))

    # features.append(map_func('head.form~head.pos~dep.form~dep.pos:%s~%s~%s~%s' % (hform, hpos, dform, dpos)))

    if h < d:
        features.append(map_func('head~head+1~dep~dep+1:%s~%s~%s~%s' % (hpos, h11pos, dpos, d11pos)))
        features.append(map_func('head~head+1~dep~dep-1:%s~%s~%s~%s' % (hpos, h11pos, dpos, d01pos)))
        features.append(map_func('head~head-1~dep~dep+1:%s~%s~%s~%s' % (hpos, h01pos, dpos, d11pos)))
        features.append(map_func('head~head-1~dep~dep-1:%s~%s~%s~%s' % (hpos, h01pos, dpos, d01pos)))
        features.append(map_func('head~head+1~head+2~dep:%s~%s~%s~%s' % (hpos, h11pos, h12pos, dpos))) #new
        features.append(map_func('head~head-1~head-2~dep:%s~%s~%s~%s' % (hpos, h01pos, h02pos, dpos))) #new

        # features.append(map_func('head~dep+1~dep~dep-1:%s~%s~%s~%s' % (hpos, d11pos, dpos, d01pos)))
        # features.append(map_func('head+1~head~head-1~dep:%s~%s~%s~%s' % (h11pos, hpos, h01pos, dpos)))
    else:
        features.append(map_func('dep~dep+1~head~head+1:%s~%s~%s~%s' % (dpos, d11pos, hpos, h11pos)))
        features.append(map_func('dep~dep+1~head~head-1:%s~%s~%s~%s' % (dpos, d11pos, hpos, h01pos)))
        features.append(map_func('dep~dep-1~head~head+1:%s~%s~%s~%s' % (dpos, d01pos, hpos, h11pos)))
        features.append(map_func('dep~dep-1~head~head-1:%s~%s~%s~%s' % (dpos, d01pos, hpos, h01pos)))
        features.append(map_func('dep~head~head+1~head+2:%s~%s~%s~%s' % (dpos, hpos, h11pos, h12pos))) #new
        features.append(map_func('dep~head~head-1~head-2:%s~%s~%s~%s' % (dpos, hpos, h01pos, h02pos))) #new
        # features.append(map_func('dep~head+1~head~head-1:%s~%s~%s~%s' % (dpos, h11pos, hpos, h01pos)))
        # features.append(map_func('dep+1~dep~dep-1~head:%s~%s~%s~%s' % (d11pos, dpos, d01pos, hpos)))


    features.append(map_func('offset:%d' % (h - d)))
    features.append(map_func('h<d~between.pos:%s' % '~'.join(map(lambda x: sent[x].pos, range(h, d+1)))))
    features.append(map_func('d<h~between.pos:%s' % '~'.join(map(lambda x: sent[x].pos, range(d, h+1)))))
    # features.append(map_func('h<d~between.pos~mor:%s' % '~'.join(map(lambda x: '%s~%s' % (sent[x].pos, sent[x].mor), range(h, d+1)))))
    # features.append(map_func('d<h~between.pos~mor:%s' % '~'.join(map(lambda x: '%s~%s' % (sent[x].pos, sent[x].mor), range(d, h+1)))))

    # morph




    if h < d:
        bpos = map(lambda x: '%s~%s' % (sent[x].pos, sent[x].mor), range(h+1, d))        
    else:
        bpos = map(lambda x: '%s~%s' % (sent[x].pos, sent[x].mor), range(d+1, h))

    for pos in bpos:
        f = 'between.pos~mor:%s' % pos
        if f not in features:
            features.append(map_func(f))


    # not helping
    # if h < d:
    #     bpos = map(lambda x: sent[x].pos, range(h, d+1))
    #     if len(bpos) > 5:
    #         bpos = bpos[:1] + bpos[-4:]

    #     features.append(map_func('h<d~between.pos:%s' % '~'.join(bpos)))
    # else:
    #     bpos = map(lambda x: sent[x].pos, range(d, h+1))
    #     if bpos > 5:
    #         bpos = bpos[:4] + bpos[-1:]
    #     features.append(map_func('d<h~between.pos:%s' % '~'.join(bpos)))




    return filter(lambda x: x, features)



def train(conll_file, model_file, epochs = 15):
    instances = []
    model = Model()
    for sent in read_sentence(open(conll_file)):
        edge_vectors = sent.get_vectors(model.register_feature)
        for d in edge_vectors:
            h = sent[d].head # not -1
            instances.append((h, edge_vectors[d]))
    model.make_weights()
    print 'model size', size(model)
    print 'instances size', size(instances)

    print 'start training ...'
    for epoch in xrange(epochs):
        correct = 0
        total = 0      
        for (gold, head_vectors) in iter(instances):
            pred = model.predict(head_vectors)
            if gold != pred:
                model.update(head_vectors[gold], head_vectors[pred])
            else:
                correct += 1
            total += 1
        print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)
        print sum(model.weights)

        # print model.weights

    model.save(model_file)
    print 'model size', size(model)
    print 'number of fearures', len(model.weights)


def train_average(conll_file, model_file, epochs = 10):
    instances = []
    model = Model()
    for sent in read_sentence(open(conll_file)):
        edge_vectors = sent.get_vectors(model.register_feature)
        for d in edge_vectors:
            h = sent[d].head # not -1
            instances.append((h, edge_vectors[d]))
    model.make_weights()
    # print 'model size', size(model)
    # print 'instances size', size(instances)
    print 'number of fearures', len(model.weights)

    print 'start training ...'

    q = 0
    for epoch in xrange(epochs):
        correct = 0
        total = 0      
        print 'start shuffle'
        random.shuffle(instances)
        print 'done shuffle'
        for (gold, head_vectors) in iter(instances):
            q += 1
            pred = model.predict(head_vectors)
            if gold != pred:
                model.update(head_vectors[gold], head_vectors[pred], q)
            else:
                correct += 1
            total += 1
        print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)

        # print model.weights
    model.average(q)
    model.save(model_file)
    # print 'model size', size(model)
    print 'number of fearures', len(model.weights)


def train_MST(conll_file, model_file, epochs = 10):
    instances = []
    model = Model()
    for sent in read_sentence(open(conll_file)):
        edge_vectors = sent.get_vectors(model.register_feature)
        edges = dict([(d, sent[d].head) for d in range(1, len(sent))])
        instances.append((edges, edge_vectors))
    model.make_weights()

    print 'start training ...'
    q = 0
    for epoch in xrange(epochs):
        correct = 0
        total = 0      
        for (gold_edges, edge_vectors) in iter(instances):
            score = sent.get_scores(model, edge_vectors)
            graph = MST(score)
            pred_edges = dict([(d,h) for (h, d) in graph.edges()])
            for d in gold_edges:
                q += 1
                gh, ph = gold_edges[d], pred_edges[d]
                if gh != ph:
                    model.update(edge_vectors[d][gh], edge_vectors[d][ph], q)
                else:
                    correct += 1
                total += 1
        print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)

    model.average(q)
    model.save(model_file)
    print 'number of fearures', len(model.weights)




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
# Graph class
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
    if flag:
        plot(g, s)
    return g

####################################################



####################################################
# helpers

# def plot(g, s):
#     # if mapping:
#     #     g = nx.relabel_nodes(g,mapping)
#     nx.write_dot(g, 'grid.dot')    
#     ga=pgv.AGraph("grid.dot")
#     ga.layout(prog='dot')
#     ga.draw('result.png')
#     os.system('open result.png')
#     for k in s:
#         if k in g.edges():
#             print k, s[k]
#     raw_input()

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


def size(o):
    t = type(o)
    if t in [str, int, float, bool]:
        return sys.getsizeof(o)
    elif t in [list, tuple]:
        return sum([size(i) for i in o])
    elif t == dict:
        return sum([size(i) for i in o.values()])
    else:
        return sum([size(i) for i in vars(o).values()])


def train_and_test(argv):
    t0 = time.time()
    train_file = argv[1]
    model_file = argv[2]
    test_file = argv[3]
    output_file = argv[4]
    train_average(train_file, model_file)

    test(test_file, model_file, output_file)
    evaluate(output_file)
    print time.time() - t0


def only_test(argv):
    model_file = argv[1]
    test_file = argv[2]
    output_file = argv[3]
    test(test_file, model_file, output_file)
    evaluate(output_file)



####################################################

if __name__ == '__main__':
    train_and_test(sys.argv)
