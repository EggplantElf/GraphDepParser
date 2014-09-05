from model import ParserModel
from feature import *
from sentence import *
from MST import *
import time

class Parser:
    def __init__(self, parser_model_file = None):
        if parser_model_file:
            self.model = ParserModel(parser_model_file)


    def __get_instances(self, model, conll_file, map_func):
        t0 = time.time()
        instances = []
        for sent in read_sentence(open(conll_file)):
            unigrams = make_unigram_features(sent)
            for d in xrange(1, len(sent)):
                head = sent[d].head
                vectors = {}
                for h in xrange(0, len(sent)):
                    if h != d:
                        vectors[h] = make_features_for_parser(sent, unigrams, h, d, map_func)
                instances.append((head, vectors))
        model.make_weights()
        print 'time used: %d' % (time.time() - t0)
        print 'num weights: %d' % len(model.weights)
        return instances


    def __get_scores_for_MST(self, sent, model, map_func):
        score = {}
        unigrams = make_unigram_features(sent)
        for d in xrange(1, len(sent)):
            for h in xrange(len(sent)):
                if h != d:
                    vector = make_features_for_parser(sent, unigrams, h, d, map_func)
                    score[(h,d)] = (model.score(vector), [(h,d)])
        return score

    def train(self, conll_file, model_file, epochs = 10):
        model = ParserModel()
        instances = self.__get_instances(model, conll_file, model.register_feature)

        print 'start training ...'
        q = 0
        for epoch in xrange(epochs):
            correct = 0
            total = 0      
            # random.shuffle(instances)
            for (gold, head_vectors) in iter(instances):
                q += 1
                pred = model.predict(head_vectors)
                if gold != pred:
                    model.update(head_vectors[gold], head_vectors[pred], q)
                else:
                    correct += 1
                total += 1
            print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)

        model.average(q)
        model.save(model_file)
        # print 'number of fearures', len(model.weights)


    def train_aggressive(self, conll_file, model_file, epochs = 10):
        model = ParserModel()
        instances = self.__get_instances(model, conll_file, model.register_feature)
        print 'start training ...'

        q = 0
        for epoch in xrange(epochs):
            correct = 0
            total = 0      
            # random.shuffle(instances)
            for (gold, head_vectors) in iter(instances):
                move_on = False
                while not move_on:
                    q += 1
                    pred = model.predict(head_vectors)
                    if gold != pred:
                        model.update(head_vectors[gold], head_vectors[pred], q)
                    else:
                        correct += 1
                        move_on = True
                    total += 1
            print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)
        model.average(q)
        model.save(model_file)
        # print 'number of fearures', len(model.weights)

    def predict(self, sent):
        score = self.__get_scores_for_MST(sent, self.model, self.model.map_feature)
        graph = MST(score)
        sent.add_heads(graph.edges())
        return sent


