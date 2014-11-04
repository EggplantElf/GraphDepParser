import sys, os, time, argparse
from model import *
from sentence import *
from multi_token_parser import *
from labeler import *


# what should the sent_instances for training be? just all arcs as in the usual way or reduced arcs which may be unsound
def train(train_file, unit_parser_model, sent_parser_model, unit_feats, sent_feats): 
    unit_parser = UnitParser() if unit_parser_model else None
    sent_parser = SentParser() if sent_parser_model else None 
    unit_instances, sent_instances = get_instances(train_file, unit_parser, sent_parser, unit_feats, sent_feats)
    if unit_parser:
        unit_parser.train(unit_instances, unit_parser_model)
    if sent_parser:
        sent_parser.train(sent_instances, sent_parser_model)

def test(conll_file, unit_parser_model, sent_parser_model, output_file, unit_feats, sent_feats, factor = 1.0):
    unit_parser = UnitParser(unit_parser_model) if unit_parser_model else None
    sent_parser = SentParser(sent_parser_model) if sent_parser_model else None
    outstream = open(output_file,'w')
    for sent in read_sentence(open(conll_file)):
        if unit_parser:
            for unit in get_units(sent):
                unit_parser.predict(sent, unit, unit_feats)
        if sent_parser:
            sent_parser.predict(sent, sent_feats, factor)
        print >> outstream, sent.to_str()
    outstream.close()


def train_CLE(train_file, unit_parser_model, sent_parser_model): 
    unit_parser = ChunkParser()
    sent_parser = SentParser()
    unit_instances, sent_instances = get_CLE_instances(train_file, \
            unit_parser.model.register_feature, sent_parser.model.register_feature)
    unit_parser.train_CLE(unit_instances, unit_parser_model)
    sent_parser.train_CLE(sent_instances, sent_parser_model)



# def train_and_test_factor(train_file, test_file, chunk_parser_model, sent_parser_model, factors):
#     # train(train_file, chunk_parser_model, sent_parser_model)
#     for f in factors:
#         test(test_file, chunk_parser_model, sent_parser_model, '../tmp/wsj_dev.pred.%.1f.conll06' % f, f)


####################################################

# todo:
# sent_parser uses partial parsed tree to get a full tree
# modify CLE?


if __name__ == '__main__':
    # train_and_test_factor('../tmp/wsj_train.cx', '../tmp/wsj_dev.cx', '../tmp/chunk.parser', '../tmp/sent.parser', [1, 1.2, 1.5, 2, 3, 5])
    # train('../tmp/wsj_train.cx', '../tmp/chunk.parser', '../tmp/sent.parser')
    # test('../tmp/wsj_dev.cx', '../tmp/chunk.parser', '../tmp/sent.parser', '../tmp/wsj_dev.chunk.pred.conll06')
    # sent_train_test('../tmp/wsj_train.cx', '../tmp/wsj_dev.cx', '../tmp/solo.parser', '../tmp/wsj_dev.solo.pred.conll06')
    # chunk_train_test('../tmp/wsj_train.cx', '../tmp/clause.parser', '../tmp/wsj_dev.cx', '../tmp/wsj_dev.clause.conll06')


    flag = sys.argv[1]

    if flag == '-baseline':
        train_file = sys.argv[2]
        sent_parser_model = sys.argv[3]
        test_file = sys.argv[4]
        output_file = sys.argv[5]
        sent_feats = 'a'
        train(train_file, None, sent_parser_model, None, sent_feats)
        test(test_file, None, sent_parser_model, output_file, None, sent_feats)
    elif flag == '-IOB':
        train_file = sys.argv[2]
        sent_parser_model = sys.argv[3]
        test_file = sys.argv[4]
        output_file = sys.argv[5]
        unit_feats = 'ab'
        sent_feats = 'ab'
        train(train_file, None, sent_parser_model, unit_feats, sent_feats)
        test(test_file, None, sent_parser_model, output_file, unit_feats, sent_feats)





