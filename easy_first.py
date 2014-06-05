from copy import deepcopy
from model import ParserModel
from feature import make_features_for_easy_parser
from sentence import *


class EasyFirstGraph:
    def __init__(self, sent, map_func, gold_arcs = []):
        assert len(sent) > 1
        # self.nodes = {} 
        self.cand_arcs = {}
        self.sent = sent
        self.pending = range(1, len(sent))
        self.selected_arcs = []

        self.allowed = []
        self.gold_arcs = gold_arcs

        self.refresh_arcs(map_func)


# important, find a way to partial update features would be much more efficiant!
# e.g. if only the words in window size of 2 of the pair are considered, can let others be the same as before!
    def refresh_arcs(self, map_func):
        # for self.pending = [1, 3, 4]
        # set self.cand_arcs = {(1,3):[fv], (3,1): [fv], (3,4): [fv], (4,3): [fv]}
        assert len(self.pending) > 0
        self.cand_arcs = {}
        for i in xrange(1, len(self.pending)):
            p, q = self.pending[i-1], self.pending[i]
            self.cand_arcs[(p, q)] = make_features_for_easy_parser(self.sent, p, q, map_func)
            self.cand_arcs[(q, p)] = make_features_for_easy_parser(self.sent, q, p, map_func)
        self.refresh_allowed()

    def is_valid(self, (h, d)):
        if (h,d) not in self.cand_arcs or (h, d) in self.selected_arcs:
            return False
        elif any(i for (i, j) in self.gold_arcs if d == i and not (d, j) in self.selected_arcs):
            return False
        else:
            return True

    def refresh_allowed(self):
        self.allowed = filter(self.is_valid, self.gold_arcs)

    def update(self, (h, d), map_func):
        self.pending.remove(d)
        self.selected_arcs.append((h, d))
        self.gold_arcs.remove((h,d))
        self.refresh_arcs(map_func)


    def predict_arc(self, model):
        # print 'cand', self.cand_arcs.keys()
        return max(self.cand_arcs, key = lambda x: model.score(self.cand_arcs[x]))

    def allow(self, arc):
        return arc in self.allowed

    # also some redundant calc here
    def best_allowed(self, model):
        # print 'allowed', self.allowed
        # if not self.allowed:
        #     print self.pending
        #     print self.gold_arcs
        #     print self.cand_arcs.keys()
        #     exit()
        if not self.allowed:
            return None
        return max(self.allowed, key = lambda x: model.score(self.cand_arcs[x]))


# not sure whether root node should be included
class EasyFirstParser:
    def __init__(self, parser_model_file = None):
        if parser_model_file:
            self.model = ParserModel(parser_model_file)

    def __get_instances(self, model, conll_file, map_func):
        instances = []
        for sent in read_sentence(open(conll_file)):
            # for n in xrange(1,len(sent)):
            #     print n, sent[n].form, sent[n].head
            gold_arcs = [(sent[d].head, d) for d in xrange(1, len(sent)) if sent[d].head != 0] # ignore root node
            # print gold_arcs
            graph = EasyFirstGraph(sent, map_func, gold_arcs)

            instances.append(graph)
        model.make_weights()
        return instances



    def train(self, conll_file, model_file, epochs = 10):
        model = ParserModel()
        map_func = model.register_feature
        instances = self.__get_instances(model, conll_file, map_func)

        print 'start training ...'
        q = 0
        for epoch in xrange(epochs):
            correct = 0
            total = 0      
            # random.shuffle(instances)
            for ori_graph in iter(instances):
                graph = deepcopy(ori_graph)
                while len(graph.pending) > 1:
                    q += 1
                    total += 1
                    pred_arc = graph.predict_arc(model)
                    print graph.pending
                    print graph.allowed
                    print graph.cand_arcs.keys()
                    print graph.gold_arcs
                    if graph.allow(pred_arc):
                        correct += 1
                        graph.update(pred_arc, map_func)
                        print 'update pred', pred_arc
                    else:
                        best_arc = graph.best_allowed(model)
                        if not best_arc:
                            print 
                            exit()
                        # print graph.cand_arcs[best_arc]
                        # print graph.cand_arcs[pred_arc]
                        model.update(graph.cand_arcs[best_arc], graph.cand_arcs[pred_arc], q)
                        graph.update(best_arc, map_func)
                        print 'update best', best_arc
            print q, correct, total
            print '\nepoch %d done, %6.2f%% correct' % (epoch,100.0*correct/total)

        model.average(q)
        model.save(model_file)


