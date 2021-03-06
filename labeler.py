from model import LabelerModel
from sentence import *
from feature import *

class Labeler:
    def __init__(self, labeler_model_file = None):
        if labeler_model_file:
            self.model = LabelerModel(labeler_model_file)


    def __get_instances(self, model, conll_file, map_func):
        instances = []
        for sent in read_sentence(open(conll_file)):
            unigrams = make_unigram_features(sent)
            for d in xrange(1, len(sent)):
                label = model.register_label(sent[d].label)
                vector = make_features_for_labeler(sent, unigrams,sent[d].head, d, model.register_feature)
                instances.append((label, vector))
        model.make_weights()
        return instances

    def train(self, conll_file, model_file, epochs = 10):
        model = LabelerModel()
        instances = self.__get_instances(model, conll_file, model.register_feature)

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

    def predict(self, sent):
        unigrams = make_unigram_features(sent)

        for d in xrange(1, len(sent)):
            h = sent[d].head
            vector = make_features_for_labeler(sent, unigrams, h, d, self.model.map_feature)
            pred = self.model.predict(vector)
            sent[d].label = self.model.mapback_label(pred)
        return sent

