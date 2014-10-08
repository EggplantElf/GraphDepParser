from model import ParserModel
from feature import *
from sentence import *
from MST import *
import time

BAD = 0

def get_chunks(sent, train = False):
    global BAD
    # make sure single token also in a list
    chunks = []
    chunk = []
    for t in range(1, len(sent)):
        if sent[t].ctag in ['B', 'O']:
            if chunk:
                chunks.append(chunk)
            chunk = [t]
        else:
            chunk.append(t)
    chunks.append(chunk)

    # in training mode, get only the "good" chunk
    if train:
        good_chunks = []
        for chunk in chunks:
            if check(sent, chunk):
                good_chunks.append(chunk)
            else:
                # print 'bad chunk!'
                # print chunk
                BAD += 1
                good_chunks.extend([[t] for t in chunk])
        chunks = good_chunks

    return chunks


def check(sent, chunk):
    return len([d for d in chunk if sent[d].head not in chunk]) == 1


def chunk_mates(chunks, token):
    mates = []
    for chunk in chunks:
        if token in chunk:
            mates = [0] + chunk[:]
            mates.remove(token)
            break
    return mates

def out_mates(sent, chunks, tid):
    for chunk in chunks:
        if tid in chunk:
            current_chunk = chunk
            break
    return [t for t in range(len(sent)) if t not in current_chunk]


def get_chunk_tokens(sent, chunks):
    # chunk_tokens = []
    # for chunk in chunks:
    #     if len(chunk) > 1:
    #         chunk_tokens += chunk
    # chunk_tokens = sum([c for c in chunks if len(c) > 1], [])
    # return chunk_tokens
    return sum([c for c in chunks if len(c) > 1], [])


def get_chunk_instances(sent, unigrams, chunk_map_func):
    chunk_instances = []
    chunks = get_chunks(sent, True)
    chunk_tokens = get_chunk_tokens(sent, chunks)
    for d in chunk_tokens:
        mates = chunk_mates(chunks, d)
        head = sent[d].head
        if head not in mates:
            head = 0
        vectors = {}
        for h in mates:
            vectors[h] = make_features_for_parser(sent, unigrams, h, d, chunk_map_func)
        chunk_instances.append((head, vectors))
    return chunk_instances

def get_sent_instances(sent, unigrams, sent_map_func):
    sent_instances = []
    for d in xrange(1, len(sent)):
        head = sent[d].head
        vectors = {}
        for h in xrange(0, len(sent)):
            if h != d:
                vectors[h] = make_features_for_parser(sent, unigrams, h, d, sent_map_func)
        sent_instances.append((head, vectors))
    return sent_instances

def get_instances(conll_file, chunk_map_func, sent_map_func):
    chunk_instances, sent_instances = [], []
    for sent in read_sentence(open(conll_file), True):
        unigrams = make_unigram_features(sent)
        if chunk_map_func:
            chunk_instances.extend(get_chunk_instances(sent, unigrams, chunk_map_func))
        # sent features should use chunk information
        if sent_map_func:
            sent_instances.extend(get_sent_instances(sent, unigrams, sent_map_func))
    return chunk_instances, sent_instances





class SentParser:
    def __init__(self, parser_model_file = None):
        if parser_model_file:
            self.model = ParserModel(parser_model_file)
        else:
            self.model = ParserModel()

    def __get_scores_for_MST(self, sent, model, map_func, factor):
        scores = {}
        unigrams = make_unigram_features(sent)    
        for d in xrange(1, len(sent)):
            # if sent[d].head in ['_', 0]:
            for h in xrange(len(sent)):
                if h != d:
                    vector = make_features_for_parser(sent, unigrams, h, d, map_func)
                    s = model.score(vector)
                    if h != 0 and h == sent[d].head and s > 0:
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


    def predict(self, sent, factor):
        score = self.__get_scores_for_MST(sent, self.model, self.model.map_feature, factor)
        graph = MST(score)
        sent.add_heads(graph.edges())
        return sent

class ChunkParser:
    def __init__(self, parser_model_file = None):
        if parser_model_file:
            self.model = ParserModel(parser_model_file)
        else:
            self.model = ParserModel()

    def __get_scores_for_MST(self, sent, chunk, model, map_func):
        score = {}
        unigrams = make_unigram_features(sent)    
        for d in chunk:
            for h in chunk + [0]:
                if h != d:
                    vector = make_features_for_parser(sent, unigrams, h, d, map_func)
                    score[(h,d)] = (model.score(vector), [(h,d)])
        return score

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



    def predict(self, sent, chunk):
        score = self.__get_scores_for_MST(sent, chunk, self.model, self.model.map_feature)
        graph = MST(score)
        sent.add_heads(graph.edges())
        return chunk


