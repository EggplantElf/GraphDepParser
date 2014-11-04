from model import ParserModel
from feature import *
# from sentence import *
from MST import *
from instance import *



class SentParser:
    def __init__(self, parser_model_file = None):
        if parser_model_file:
            self.model = ParserModel(parser_model_file)
        else:
            self.model = ParserModel()

    def __get_scores_for_MST(self, sent, model, map_func, factor = 1):
        scores = {}
        unigrams = make_unigram_features(sent)    
        for d in xrange(1, len(sent)):
            for h in xrange(len(sent)):
                if h != d:
                    vector = make_features_for_parser(sent, unigrams, h, d, map_func, chunk_info = False)
                    s = model.score(vector)
                    if h != 0 and h == sent[d].chunkhead and s > 0:
                        s *= factor
                    scores[(h,d)] = (s, [(h,d)])
        return scores


    def train(self, instances, model_file, epochs = 10):
        print 'start training ...'
        self.model.make_weights()
        q = 0
        for epoch in xrange(epochs):
            correct = 0
            total = 0      
            for (gold, head_vectors) in iter(instances):
                q += 1
                pred = self.model.predict(head_vectors)
                if gold != pred:
                    self.model.update(head_vectors[gold], head_vectors[pred], q)
                else:
                    correct += 1
                total += 1
            print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)

        self.model.average(q)
        self.model.save(model_file)

    def predict(self, sent):
        score = self.__get_scores_for_MST(sent, self.model, self.model.map_feature)
        graph = MST(score)
        sent.add_heads(graph.edges())
        return sent

    def predict_with_factor(self, sent, factor):
        score = self.__get_scores_for_MST(sent, self.model, self.model.map_feature, factor)
        graph = MST(score)
        sent.add_heads(graph.edges())
        return sent

    def train_CLE(self, instances, model_file, epochs = 10):
        print 'start training ...'
        self.model.make_weights()
        q = 0
        for epoch in xrange(epochs):
            correct = 0
            total = 0      
            for (gold_arcs, vectors) in iter(instances):
                q += 1
                scores = {}
                for a in vectors:
                    scores[a] = (self.model.score(vectors[a]), [a])
                pred_arcs = MST(scores).edges()
                gold_heads = dict([(d, h) for (h, d) in gold_arcs])
                pred_heads = dict([(d, h) for (h, d) in pred_arcs])
                for d in gold_heads:
                    if gold_heads[d] != pred_heads[d]:
                        self.model.update(vectors[(gold_heads[d], d)], vectors[(pred_heads[d], d)], q)
                    else:
                        correct += 1
                    total += 1
            print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)
        self.model.average(q)
        self.model.save(model_file)







class ChunkParser:
    def __init__(self, parser_model_file = None):
        if parser_model_file:
            self.model = ParserModel(parser_model_file)
        else:
            self.model = ParserModel()

    def __get_scores_for_MST(self, sent, chunk, model, map_func):
        scores = {}
        unigrams = make_unigram_features(sent)    
        for d in chunk:
            for h in chunk + [0]:
                if h != d:
                    vector = make_features_for_parser(sent, unigrams, h, d, map_func)
                    scores[(h,d)] = (model.score(vector), [(h,d)])
        return scores

    def train(self, instances, model_file, epochs = 10):
        self.model.make_weights()
        print 'start training ...'
        q = 0
        for epoch in xrange(epochs):
            correct = 0
            total = 0      
            for (gold, head_vectors) in iter(instances):
                q += 1
                pred = self.model.predict(head_vectors)
                if gold != pred:
                    self.model.update(head_vectors[gold], head_vectors[pred], q)
                else:
                    correct += 1
                total += 1
            print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)

        self.model.average(q)
        self.model.save(model_file)


    # def train_CLE(self, instances, model_file, epoch = 10):
    #     self.model.make_weights()
    #     for epoch in xrange(epochs):
    #         correct = 0
    #         total = 0
    #         for sent in instances:

    def train_CLE(self, instances, model_file, epochs = 10):
        print 'start training ...'
        self.model.make_weights()
        q = 0
        for epoch in xrange(epochs):
            correct = 0
            total = 0      
            for (gold_arcs, vectors) in iter(instances):
                q += 1
                scores = {}
                for a in vectors:
                    scores[a] = (self.model.score(vectors[a]), [a])
                pred_arcs = MST(scores).edges()
                gold_heads = dict([(d, h) for (h, d) in gold_arcs])
                pred_heads = dict([(d, h) for (h, d) in pred_arcs])
                for d in gold_heads:
                    if gold_heads[d] != pred_heads[d]:
                        self.model.update(vectors[(gold_heads[d], d)], vectors[(pred_heads[d], d)], q)
                    else:
                        correct += 1
                    total += 1
            print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)
        self.model.average(q)
        self.model.save(model_file)


    def predict(self, sent, chunk):
        score = self.__get_scores_for_MST(sent, chunk, self.model, self.model.map_feature)
        graph = MST(score)
        sent.add_chunkheads(graph.edges())
        # use to check chunk accuracy
        # sent.add_heads(graph.edges())
        return sent


