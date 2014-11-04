from sentence import *
from feature import *

def get_chunks(sent, train = False):
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
                good_chunks.extend([[t] for t in chunk])
        chunks = good_chunks

    # only return chunks with more than one token
    return filter(lambda x: len(x) > 1, chunks)

def get_clauses(sent, train = False):
    # use the output of the chunker, label O as the clause boundary
    clauses = []
    clause = []
    for t in range(1, len(sent)):
        if sent[t].ctag == 'O':
            if clause:
                clauses.append(clause)
            clause = []
        else:
            clause.append(t)
    # special treatment for train mode?
    if train:
        pass
    return filter(lambda x: len(x) > 1, clauses)


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
    return sum([c for c in chunks if len(c) > 1], [])

def get_chunk_instances(sent, chunks, unigrams, chunk_map_func):
    chunk_instances = []
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

def get_sent_instances(sent, chunks, unigrams, sent_map_func):
    sent_instances = []
    for d in xrange(1, len(sent)):
        head = sent[d].head
        # d in a chunk, need test
        if any(c for c in chunks if d in c and sent[d].head in c):
            sent[d].chunkhead = sent[d].head
        vectors = {}
        for h in xrange(0, len(sent)):
            if h != d:
                vectors[h] = make_features_for_parser(sent, unigrams, h, d, sent_map_func, chunk_info = False)
        sent_instances.append((head, vectors))
    return sent_instances

def get_instances(conll_file, chunk_map_func, sent_map_func):
    chunk_instances, sent_instances = [], []
    for sent in read_sentence(open(conll_file), True):
        unigrams = make_unigram_features(sent)
        good_chunks = get_chunks(sent, True)
        chunks = get_chunks(sent, False)        
        # good_chunks = get_clauses(sent, True)
        # chunks = get_clauses(sent, False)
        if chunk_map_func:
            chunk_instances.extend(get_chunk_instances(sent, good_chunks, unigrams, chunk_map_func))
        if sent_map_func:
            sent_instances.extend(get_sent_instances(sent, chunks, unigrams, sent_map_func))

    return chunk_instances, sent_instances



def get_CLE_chunk_instance(sent, chunk, unigrams, sent_map_func):
    arcs = []
    vectors = {}
    for d in chunk:
        arcs.append((sent[d].head if sent[d].head in chunk else 0, d))
        for h in [0] + chunk:
            if h != d:
                vectors[(h, d)] = make_features_for_parser(sent, unigrams, h, d, sent_map_func)
    return arcs, vectors


def get_CLE_sent_instance(sent, chunks, unigrams, sent_map_func):
    # chunks are used as feature
    arcs = []
    vectors = {}
    for d in xrange(1, len(sent)):
        arcs.append((sent[d].head, d))
        # if any(c for c in chunks if d in c and sent[d].head in c):
            # sent[d].chunkhead = sent[d].head
        for h in xrange(0, len(sent)):
            if h != d:
                vectors[(h, d)] = make_features_for_parser(sent, unigrams, h, d, sent_map_func)
    return arcs, vectors


def get_CLE_instances(conll_file, chunk_map_func, sent_map_func):
    chunk_instances, sent_instances = [], []
    for sent in read_sentence(open(conll_file), True):
        unigrams = make_unigram_features(sent)
        # only good chunks for training
        chunks = get_chunks(sent, True)
        for chunk in chunks:
            chunk_instances.append(get_CLE_chunk_instance(sent, chunk, unigrams, chunk_map_func))
        sent_instances.append(get_CLE_sent_instance(sent, chunks, unigrams, sent_map_func))
    return chunk_instances, sent_instances



