import sys, os, time, argparse
from model import *
from sentence import *
from multi_token_parser import *
from labeler import *


# what should the sent_instances for training be? just all arcs as in the usual way or reduced arcs which may be unsound
def train(train_file, chunk_parser_model, sent_parser_model): 
    chunk_parser = ChunkParser()
    sent_parser = SentParser()
    chunk_instances, sent_instances = get_instances(train_file, \
            chunk_parser.model.register_feature, sent_parser.model.register_feature)
    chunk_parser.train(chunk_instances, chunk_parser_model)
    sent_parser.train(sent_instances, sent_parser_model)

def test(conll_file, chunk_parser_model, sent_parser_model, output_file, factor = 2):
    chunk_parser = ChunkParser(chunk_parser_model)
    sent_parser = SentParser(sent_parser_model)
    outstream = open(output_file,'w')
    for sent in read_sentence(open(conll_file)):
        for chunk in get_chunks(sent):
            if len(chunk) > 1:
                chunk_parser.predict(sent, chunk)

        sent_parser.predict(sent, factor)
        print >> outstream, sent.to_str()
    outstream.close()

# def sent_train_test(train_file, test_file, sent_parser_model, output_file):
#     sent_parser = SentParser()
#     chunk_instances, sent_instances = get_instances(train_file, None, sent_parser.model.register_feature)
#     sent_parser.train(sent_instances, sent_parser_model)
#     outstream = open(output_file,'w')
#     for sent in read_sentence(open(test_file)):
#         sent_parser.predict(sent)
#         print >> outstream, sent.to_str()
#     outstream.close()

# def chunk_train_test(train_file, test_file, chunk_parser_model, output_file):
#     chunk_parser = ChunkParser()
#     chunk_instances, sent_instances = get_instances(train_file, chunk_parser.model.register_feature, None)
#     chunk_parser.train(chunk_instances, chunk_parser_model)
#     outstream = open(output_file,'w')
#     for sent in read_sentence(open(test_file)):
#         for chunk in get_chunks(sent):
#             if len(chunk) > 1:
#                 chunk_parser.predict(sent, chunk)
#         print >> outstream, sent.to_str()
#     outstream.close()

def train_and_test_factor(train_file, test_file, chunk_parser_model, sent_parser_model, factors):
    # train(train_file, chunk_parser_model, sent_parser_model)
    for f in factors:
        test(test_file, chunk_parser_model, sent_parser_model, '../tmp/wsj_dev.pred.%.1f.conll06' % f, f)


####################################################

# todo:
# sent_parser uses partial parsed tree to get a full tree
# modify CLE?


if __name__ == '__main__':
    train_and_test_factor('../tmp/wsj_train.cx', '../tmp/wsj_dev.cx', '../tmp/chunk.parser', '../tmp/sent.parser', [1, 1.2, 1.5, 2, 3, 5])
    # train('../tmp/wsj_train.cx', '../tmp/chunk.parser', '../tmp/sent.parser')
    # test('../tmp/wsj_dev.cx', '../tmp/chunk.parser', '../tmp/sent.parser', '../tmp/wsj_dev.pred.conll06')
    # sent_train_test('../tmp/wsj_train.cx', '../tmp/wsj_dev.cx', '../tmp/solo.parser', '../tmp/wsj_dev.solo.pred.conll06')
    # chunk_train_test('../tmp/wsj_full_train.cx', '../tmp/wsj_dev.cx', '../tmp/chunk.parser', '../tmp/wsj_dev.chunk.conll06')


