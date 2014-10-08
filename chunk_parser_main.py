import sys, time, argparse
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

def test(conll_file, chunk_parser_model, sent_parser_model, output_file):
    chunk_parser = ChunkParser(chunk_parser_model)
    sent_parser = SentParser(sent_parser_model)
    outstream = open(output_file,'w')
    for sent in read_sentence(open(conll_file)):
        for chunk in get_chunks(sent):
            if len(chunk) > 1:
                chunk_parser.predict(sent, chunk)

        sent_parser.predict(sent)
        print >> outstream, sent.to_str()
    outstream.close()

def no_chunk_train_test(train_file, test_file, sent_parser_model, output_file):
    sent_parser = SentParser()
    sent_instances = get_instances(train_file, sent_parser.model.register_feature)
    sent_parser.train(sent_instances, sent_parser_model)
    outstream = open(output_file,'w')
    for sent in read_sentence(open(test_file)):
        sent_parser.predict(sent)
        print >> outstream, sent.to_str()
    outstream.close()


####################################################

# todo:
# sent_parser uses partial parsed tree to get a full tree
# modify CLE?


if __name__ == '__main__':
    # train('../tmp/wsj_train.cx', '../tmp/chunk.parser', '../tmp/sent.parser')
    test('../tmp/wsj_dev.cx', '../tmp/chunk.parser', '../tmp/sent.parser', '../tmp/wsj_dev.pred.conll06')
    # no_chunk_train_test('../tmp/wsj_train.cx', '../tmp/wsj_dev.cx', '../tmp/solo.parser', '../tmp/wsj_dev.solo.pred.conll06')