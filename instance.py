from sentence import *
from feature import *

def get_chunks(sent, train = False):
    # make sure single token also in a list
    chunks = []
    chunk = []
    for t in range(1, len(sent)):
        if sent[t].ctag[0] in ['B', 'O']:
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
        good_clauses = []
        for clause in clauses:
            if check(sent, clause):
                good_clauses.append(clause)
            else:
                good_clauses.extend([[t] for t in clause])
        clauses = good_clauses
    return filter(lambda x: len(x) > 1, clauses)


def check(sent, unit):
    return len([d for d in unit if sent[d].head not in unit]) == 1


def unit_mates(units, token):
    mates = []
    for unit in units:
        if token in unit:
            mates = [0] + unit[:]
            mates.remove(token)
            break
    return mates

def out_mates(sent, units, tid):
    for unit in units:
        if tid in unit:
            current_unit = unit
            break
    return [t for t in range(len(sent)) if t not in current_unit]


def get_unit_tokens(sent, units):
    return sum([c for c in units if len(c) > 1], [])

def get_unit_instances(sent, units, unigrams, unit_map_func, feats):
    unit_instances = []
    unit_tokens = get_unit_tokens(sent, units)
    for d in unit_tokens:
        mates = unit_mates(units, d)
        head = sent[d].head
        if head not in mates:
            head = 0
        vectors = {}
        for h in mates:
            vectors[h] = make_features_for_parser(sent, unigrams, h, d, unit_map_func, feats)
        unit_instances.append((head, vectors))
    return unit_instances

def get_sent_instances(sent, units, unigrams, sent_map_func, feats):
    sent_instances = []
    for d in xrange(1, len(sent)):
        head = sent[d].head
        # d in a unit, need test
        # what does this line mean?
        if any(c for c in units if d in c and sent[d].head in c):
            sent[d].unithead = sent[d].head
        vectors = {}
        for h in xrange(0, len(sent)):
            if h != d:
                vectors[h] = make_features_for_parser(sent, unigrams, h, d, sent_map_func, feats)
        sent_instances.append((head, sent[d].unithead, vectors))
    return sent_instances

def get_instances(conll_file, unit_parser, sent_parser, unit_feats, sent_feats, unit_type = '-chunk'):
    unit_instances, sent_instances = [], []
    get_units = get_chunks if unit_type == '-chunk' else get_clauses
    for sent in read_sentence(open(conll_file), True):
        unigrams = make_unigram_features(sent)
        good_units = get_units(sent, True)
        units = get_units(sent, False)
        if unit_parser:
            unit_instances.extend(get_unit_instances(sent, good_units, unigrams, unit_parser.model.register_feature, unit_feats))
        if sent_parser:
            sent_instances.extend(get_sent_instances(sent, units, unigrams, sent_parser.model.register_feature, sent_feats))

    return unit_instances, sent_instances



# def get_CLE_chunk_instance(sent, chunk, unigrams, sent_map_func):
#     arcs = []
#     vectors = {}
#     for d in chunk:
#         arcs.append((sent[d].head if sent[d].head in chunk else 0, d))
#         for h in [0] + chunk:
#             if h != d:
#                 vectors[(h, d)] = make_features_for_parser(sent, unigrams, h, d, sent_map_func)
#     return arcs, vectors


# def get_CLE_sent_instance(sent, chunks, unigrams, sent_map_func):
#     # chunks are used as feature
#     arcs = []
#     vectors = {}
#     for d in xrange(1, len(sent)):
#         arcs.append((sent[d].head, d))
#         # if any(c for c in chunks if d in c and sent[d].head in c):
#             # sent[d].chunkhead = sent[d].head
#         for h in xrange(0, len(sent)):
#             if h != d:
#                 vectors[(h, d)] = make_features_for_parser(sent, unigrams, h, d, sent_map_func)
#     return arcs, vectors


# def get_CLE_instances(conll_file, chunk_map_func, sent_map_func):
#     chunk_instances, sent_instances = [], []
#     for sent in read_sentence(open(conll_file), True):
#         unigrams = make_unigram_features(sent)
#         # only good chunks for training
#         chunks = get_chunks(sent, True)
#         for chunk in chunks:
#             chunk_instances.append(get_CLE_chunk_instance(sent, chunk, unigrams, chunk_map_func))
#         sent_instances.append(get_CLE_sent_instance(sent, chunks, unigrams, sent_map_func))
#     return chunk_instances, sent_instances



