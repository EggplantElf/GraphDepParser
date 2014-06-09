from copy import copy
from model import ParserModel
from feature import make_features_for_easy_parser
from sentence import *


class EasyFirstGraph:
    def __init__(self, sent = None, map_func = None, gold_arcs = [], max_dist = 0, clone = False):
        if not clone:
            self.max_dist = max_dist
            self.cand_arcs = {}
            self.sent = sent
            self.pending = range(1, len(sent))
            self.map_func = map_func

            self.sorted_cands = []
            self.allowed = []
            self.gold_arcs = gold_arcs

            self.refresh_cands()
            if gold_arcs:
                self.refresh_allowed()


    def clone(self):
        g = EasyFirstGraph(clone = True)
        g.max_dist = self.max_dist
        g.sent = self.sent
        g.sorted_cands = []
        g.map_func = self.map_func

        g.pending = copy(self.pending)
        g.cand_arcs = copy(self.cand_arcs)
        g.allowed = copy(self.allowed)
        g.gold_arcs = copy(self.gold_arcs)
        return g

    # used both in predict and training
    def update(self, (h, d),  train = True):
        self.pending.remove(d)
        self.refresh_cands()
        if train:
            self.gold_arcs.remove((h,d))
            self.refresh_allowed()

# important, find a way to partial update features would be much more efficiant!
# e.g. if only the words in window size of 2 of the pair are considered, can let others be the same as before!
    def refresh_cands(self):
        # for self.pending = [1, 3, 4]
        # set self.cand_arcs = {(1,3):[fv], (3,1): [fv], (3,4): [fv], (4,3): [fv]}
        assert len(self.pending) > 0
        self.cand_arcs = {}
            # p, q = self.pending[i-1], self.pending[i]
            # self.cand_arcs[(p, q)] = make_features_for_easy_parser(self.sent, p, q, map_func)
            # self.cand_arcs[(q, p)] = make_features_for_easy_parser(self.sent, q, p, map_func)
        for i in xrange(self.max_dist + 1):
            for j in xrange(i + 1, len(self.pending)):
                # i = 0 to max_dist, j = i + 1 to end
                p, q = self.pending[j - i - 1], self.pending[j]
                self.cand_arcs[(p, q)] = make_features_for_easy_parser(self.sent, self, p, q, self.map_func)
                self.cand_arcs[(q, p)] = make_features_for_easy_parser(self.sent, self, q, p, self.map_func)


    def predict_arc(self, model):
        self.sorted_cands = sorted(self.cand_arcs, key = lambda x: model.score(self.cand_arcs[x]), reverse = True)
        return self.sorted_cands[0]

    # used only in training
    def refresh_allowed(self):
        self.allowed = filter(self.__gold_is_valid, self.gold_arcs)

    def __gold_is_valid(self, (h, d)):
        return (h,d) in self.cand_arcs and all(i != d for (i, j) in self.gold_arcs)

    def __gold_is_valid_no_dist(self, (h,d)):
        return all(i != d for (i, j) in self.gold_arcs)

    def allow(self, arc):
        return arc in self.allowed

    # compute the current non-project distance of the arc, from 0
    def __dist(self, arc):
        return self.pending.index(max(arc)) - self.pending.index(min(arc)) - 1

    # use sorted_allowed is still a little redundant in prediction
    def best_allowed(self):
        sorted_by_score = filter(lambda x: x in self.allowed, self.sorted_cands)
        sorted_by_dist = sorted(sorted_by_score, key = self.__dist, reverse = True)
        if sorted_by_dist:
            return sorted_by_dist[0]
        else:
            # if non-proj distance to long then choose the shortest from gold_arcs
            # print self.pending
            # print self.gold_arcs
            # print self.cand_arcs.keys()
            # print min(filter(self.__gold_is_valid_no_dist, self.gold_arcs), key = self.__dist)
            try:
                return min(filter(self.__gold_is_valid_no_dist, self.gold_arcs), key = self.__dist)
            except:
                print self.pending
                print self.gold_arcs
                print self.cand_arcs.keys()
                for t in self.sent:
                    print t.form
                exit()

# not sure whether root node should be included
class EasyFirstParser:
    def __init__(self, parser_model_file = None, max_dist = 0):
        self.max_dist = max_dist
        if parser_model_file:
            self.model = ParserModel(parser_model_file)

    def __get_instances(self, model, conll_file, map_func):
        instances = []
        for sent in read_sentence(open(conll_file)):
            gold_arcs = [(sent[d].head, d) for d in xrange(1, len(sent)) if sent[d].head != 0] # ignore root node
            graph = EasyFirstGraph(sent, map_func, gold_arcs, self.max_dist)
            instances.append(graph)
        model.make_weights()
        return instances



    def train(self, conll_file, model_file, epochs = 10):
        model = ParserModel()
        instances = self.__get_instances(model, conll_file, model.register_feature)

        print 'start training ...'
        q = 0
        for epoch in xrange(epochs):
            correct = 0
            total = 0      
            # random.shuffle(instances)
            count = 0
            for ori_graph in iter(instances):
                # count += 1
                # if count % 100 == 0:
                #     print count
                graph = ori_graph.clone()
                while graph.gold_arcs:
                    q += 1
                    total += 1
                    pred_arc = graph.predict_arc(model)
                    if graph.allow(pred_arc):
                        correct += 1 
                        graph.update(pred_arc)
                        # print 'update pred', pred_arc
                    else:
                        best_arc = graph.best_allowed()
                        # only update the model if the best_arc is possible in the current state
                        if best_arc in graph.cand_arcs:
                            model.update(graph.cand_arcs[best_arc], graph.cand_arcs[pred_arc], q)
                        graph.update(best_arc)
                        # print 'update best', best_arc
            print q, correct, total
            print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)

        model.average(q)
        model.save(model_file)

    def predict(self, sent):
        graph = EasyFirstGraph(sent, self.model.map_feature, [], self.max_dist)
        arcs = []
        while len(graph.pending) > 1:
            pred_arc = graph.predict_arc(self.model)
            arcs.append(pred_arc)
            graph.update(pred_arc, False)
        arcs.append((0, graph.pending[0]))
        sent.add_heads(arcs)
        return sent

