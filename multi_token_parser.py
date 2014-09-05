from scipy import sparse, ones, zeros
import numpy as np
from model import ParserModel
from feature import *
from sentence import *
from MST import *
import time

def chunk_mates(chunks, token):
    mates = []
    for chunk in chunks:
        if token in chunk:
            mates = [0] + chunk[:]
            mates.remove(token)
            break
    return mates

def non_chunk_mate(sent, chunks, token):
    mates = []
    exclude = set()
    for chunk in chunks:
        if token in chunk:
            exclude = set(chunk)
            break
    return list(set(sent) - exclude)


def check(sent, chunk):
    return len([d for d in chunk if sent[d].head not in chunk]) == 1

def devide(sent, chunks):
    chunk_tokens = sum(chunks, [])
    non_head_chunk_tokens = []
    for chunk in chunks:
        non_head_chunk_tokens += [d for d in chunk if sent[d].head in chunk]

    out_tokens = list(set(sent[1:]) - set(non_head_chunk_tokens))
    return chunk_tokens, out_tokens


# should integrate the chunker with the input format conll
def get_instances(chunker, conll_file, chunk_map_func, sent_map_func, train = True):
    chunk_instances, sent_instances = [], []
    for sent in read_sentence(open(conll_file)):
        unigrams = make_unigram_features(sent)
        chunks = chunker.chunk(sent)
        # sanity check for gold tree, also can contain statistics for further analysis
        if train:
            good_chunks = []
            for chunk in chunks:
                if check(sent, chunk):
                    good_chunks.append(chunk)
                else:
                    print 'bad chunk!'
            chunks = good_chunks

        chunk_tokens, out_tokens = devide(sent, chunks)

        # a sentence is chunked as [[1, 2], 3, [4, 5, 6, 7]]
        # [1, 2, 4, 5, 6, 7]
        for d in chunk_tokens:
            mates = chunk_mates(chunks, d)
            head = sent[d].head
            vectors = {}
            for h in mates:
                vectors[h] = make_features_for_parser(sent, unigrams, h, d, map_func)
            chunk_instances.append((head, vectors))

        # [2, 3, 5]
        for d in out_tokens:
            mates = non_chunk_mates(chunks, d)
            head = sent[d].head
            vectors = {}
            for h in mates:
                vectors[h] = make_features_for_parser(sent, unigrams, h, d, map_func)
            sent_instances.append((head, vectors))

    return chunk_instances, sent_instances


class SentParser:
    def __init__(self, parser_model_file = None):
        if parser_model_file:
            self.model = ParserModel(parser_model_file)


    def __get_scores_for_MST(self, sent, model, map_func):
        score = {}
        unigrams = make_unigram_features(sent)    
        for d in xrange(1, len(sent)):
            if sent[d].phead == '_':
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

    def predict(self, sent):
        score = self.__get_scores_for_MST(sent, self.model, self.model.map_feature)
        graph = MST(score)
        sent.add_heads(graph.edges())
        return sent

class ChunkParser:
    def __init__(self, parser_model_file = None):
        if parser_model_file:
            self.model = ParserModel(parser_model_file)

    def __get_scores_for_MST(self, sent, model, map_func):
        score = {}
        unigrams = make_unigram_features(sent)    
        for d in xrange(1, len(sent)):
            if sent[d].phead == '_':
                for h in xrange(len(sent)):
                    if h != d:
                        vector = make_features_for_parser(sent, unigrams, h, d, map_func)
                        score[(h,d)] = (model.score(vector), [(h,d)])
        return score

    def predict(self, chunk):
        score = self.__get_scores_for_MST(chunk, self.model, self.model.map_feature)
        graph = MST(score)
        chunk.add_heads(graph.edges())


