import gzip, cPickle, math
from itertools import imap
# from sentence import *

class ParserModel:
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
        self.__drop_zero_features()
        cPickle.dump(self.weights,stream,-1)
        cPickle.dump(self.featmap,stream,-1)
        stream.close()


    def __drop_zero_features(self):
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
        else:
            return self.featmap[feature]

    def map_feature(self, feature):
        return self.featmap.get(feature,None)

    def __select_weight(self, x):
        # avoid overuse of lambda
        return self.weights[x - 1]

    def score(self, vector):
        return sum(imap(self.__select_weight, vector))

    # should be more generalized, and don't use lambda
    def predict(self, vectors):
        return max(vectors, key = lambda h: self.score(vectors[h]))

    def update(self, gold_feat, pred_feat, q = 1):
        for i in gold_feat:
            self.weights[i-1] += 1
            self.delta[i-1] += q
        for i in pred_feat:
            self.weights[i-1] -= 1
            self.delta[i-1] -= q

    def average(self, q):
        for i in xrange(len(self.weights)):
            self.weights[i] -= self.delta[i] / q


class LabelerModel:
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

# need modify
    def __drop_zero_features(self):
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
            for i in xrange(len(self.weights)):
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
        return sum(imap(lambda x: self.weights[x - 1], vector))

    def predict(self, vector):
        ans = 0
        maxsum = -9999
        for i in xrange(len(self.labelmap)):
            s = sum(imap(lambda x: self.weights[i][x-1], vector))
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
        for i in xrange(len(self.weights)):
            for j in xrange(len(self.weights[i])):
                self.weights[i][j] -= self.delta[i][j] / q
