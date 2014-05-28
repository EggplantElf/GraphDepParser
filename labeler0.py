import sys, os, cPickle, gzip, math, time
from model import *
from sentence import *
from train import *


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
        self.phead = entries[8]
        self.plabel = '<NA>'

    def to_str(self):
        return '%d\t%s\t%s\t%s\t_\t_\t%d\t%s\t%s\t%s' %\
            (self.tid, self.form, self.lemma, self.pos, self.head, self.label, self.phead, self.plabel)

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

    def to_str(self):
        return '\n'.join([self[i].to_str() for i in range(1, len(self))]) + '\n'


class Model:
    def __init__(self, modelfile = None):
        self.featmap = {}
        self.labelmap = {}
        self.label_revmap = {}
        self.weights = []
        self.delta = []
        if modelfile:
            self.load(modelfile)

    def make_weights(self):
        numfeatures = len(self.featmap)
        numlabels = len(self.labelmap)
        self.weights = [ [ 0.0 for f in xrange(numfeatures) ] for l in xrange(numlabels) ]
        self.delta = [ [ 0.0 for f in xrange(numfeatures) ] for l in xrange(numlabels) ]

    def save(self, modelfile):
        stream = gzip.open(modelfile,'wb')
        # self.drop_zero_features()
        cPickle.dump(self.weights,stream,-1)
        cPickle.dump(self.featmap,stream,-1)
        cPickle.dump(self.labelmap, stream, -1)
        cPickle.dump(self.label_revmap, stream, -1)
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
        self.labelmap = cPickle.load(stream)
        self.label_revmap = cPickle.load(stream)
        stream.close()

    def numfeatures(self):
        return len(self.featmap)

    def register_feature(self, feature):
        if feature not in self.featmap:
            self.featmap[feature] = self.numfeatures()+1
            for i in range(len(self.weights)):
                self.weights[i].append(0.0)
                self.delta[i].append(0.0)
            return self.numfeatures()
        else:
            return self.featmap[feature]

    def map_feature(self, feature):
        return self.featmap.get(feature,None)

    def register_label(self, label):
        numfeatures = self.numfeatures()
        if label not in self.labelmap:
            self.labelmap[label] = len(self.labelmap) + 1
            self.label_revmap[len(self.labelmap)] = label
            self.weights.append([ 0.0 for f in xrange(numfeatures) ])
            self.delta.append([ 0.0 for f in xrange(numfeatures) ])
            return len(self.labelmap)
        else:
            return self.labelmap[label]

    def map_label(self, label):
        return self.labelmap.get(label, None)

    def mapback_label(self, label_int):
        return self.label_revmap.get(label_int, None)

    def score(self, vector):
        return sum(map(lambda x: self.weights[x - 1], vector))

    def predict(self, vector):
        ans = 0
        maxsum = -9999
        for i in range(len(self.labelmap)):
            s = sum(map(lambda x: self.weights[i][x-1], vector))
            if s > maxsum:
                maxsum = s
                ans = i + 1
        return ans


    def update(self, vector, gold, pred, q = 1):
        for i in vector:
            self.weights[gold - 1][i-1] += 1
            self.delta[gold - 1][i-1] += q

            self.weights[pred-1][i-1] -= 1
            self.delta[pred-1][i-1] -= q

    def average(self, q):
        for i in range(len(self.weights)):
            for j in range(len(self.weights[i])):
                self.weights[i][j] -= self.delta[i][j] / q
        # print self.weights[:30]

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
        features.append(map_func('h.pos~d.pos:%s~%s' % (hpos, dpos)))
        features.append(map_func('h.pos~d.form:%s~%s' % (hpos, dform)))
        features.append(map_func('h.form~d.pos:%s~%s' % (hform, dpos)))
        features.append(map_func('h.mor~d.mor:%s~%s' % (hmor, dmor)))
        features.append(map_func('h.mor~h.pos~d.mor~d.pos:%s~%s~%s~%s' % (hmor, hpos, dmor, dpos)))

    else:
        features.append(map_func('d.pos~h.pos:%s~%s' % (dpos, hpos)))
        features.append(map_func('d.pos~h.form:%s~%s' % (dpos, hform)))
        features.append(map_func('d.form~h.pos:%s~%s' % (dform, hpos)))
        features.append(map_func('d.mor~h.mor:%s~%s' % (dmor, hmor)))
        features.append(map_func('d.mor~d.pos~h.mor~h.pos:%s~%s~%s~%s' % (dmor, dpos, hmor, hpos)))

    return filter(lambda x: x, features)

def train_average(conll_file, model_file, epochs = 10):
    instances = []
    model = Model()
    for sent in read_sentence(open(conll_file)):
        for d in range(1, len(sent)):
            label = model.register_label(sent[d].label)
            h = sent[d].head
            vector = make_features(sent, h, d, model.register_feature)
            instances.append((label, vector))

    model.make_weights()

    print 'number of fearures', len(model.featmap)

    print 'start training ...'
    q = 0
    for epoch in xrange(epochs):
        correct = 0
        total = 0      
        # random.shuffle(instances)
        for (gold, vector) in iter(instances):
            q += 1
            pred = model.predict(vector)
            if gold != pred:
                model.update(vector, gold, pred, q)
            else:
                correct += 1
            total += 1
        print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)

    model.average(q)
    model.save(model_file)


def test(conll_file, model_file, output_file):
    outstream = open(output_file,'w')
    model = Model(model_file)
    for sent in read_sentence(open(conll_file)):
        for d in range(1, len(sent)):
            h = sent[d].head
            vector = make_features(sent, h, d, model.map_feature)
            pred = model.predict(vector)
            sent[d].plabel = model.mapback_label(pred)
        print >> outstream, sent.to_str()

    outstream.close()


def train_and_test(argv):
    t0 = time.time()
    train_file = argv[1]
    model_file = argv[2]
    test_file = argv[3]
    output_file = argv[4]
    train_average(train_file, model_file)

    test(test_file, model_file, output_file)
    # evaluate(output_file)
    print time.time() - t0


if __name__ == '__main__':
    train_and_test(sys.argv)