import sys, os, time, argparse
from model import *
from sentence import *
from multi_token_parser import *
from labeler import *


# what should the sent_instances for training be? just all arcs as in the usual way or reduced arcs which may be unsound
def train(train_file, unit_parser_model, sent_parser_model, unit_feats, sent_feats, unit_type = '-chunk', factor = 1.0): 
    unit_parser = UnitParser() if unit_parser_model else None
    sent_parser = SentParser() if sent_parser_model else None 
    unit_instances, sent_instances = get_instances(train_file, unit_parser, sent_parser, unit_feats, sent_feats, unit_type)
    if unit_parser:
        unit_parser.train(unit_instances, unit_parser_model)
    if sent_parser:
        sent_parser.train(sent_instances, sent_parser_model, factor=factor)

def test(conll_file, unit_parser_model, sent_parser_model, output_file, unit_feats, sent_feats, unit_type = '-chunk', factor = 1.0):
    unit_parser = UnitParser(unit_parser_model) if unit_parser_model else None
    sent_parser = SentParser(sent_parser_model) if sent_parser_model else None
    get_units = get_chunks if unit_type == '-chunk' else get_clauses
    outstream = open(output_file,'w')
    for sent in read_sentence(open(conll_file)):
        if unit_parser:
            # get_chunk or get_clause
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



####################################################

# todo:
# sent_parser uses partial parsed tree to get a full tree
# modify CLE?


if __name__ == '__main__':

    flag = sys.argv[1]
    mode = sys.argv[2]

    if flag == '-baseline':
        sent_feats = 'a'    
        if mode == '-train':
            train_file = sys.argv[3]
            sent_parser_model = sys.argv[4]
            train(train_file, None, sent_parser_model, None, sent_feats)
        elif mode == '-test':
            test_file = sys.argv[3]
            sent_parser_model = sys.argv[4]
            output_file = sys.argv[5]
            test(test_file, None, sent_parser_model, output_file, None, sent_feats)

    elif flag == '-IOB':
        sent_feats = 'ab'
        if mode == '-train':
            train_file = sys.argv[3]
            sent_parser_model = sys.argv[4]
            train(train_file, None, sent_parser_model, None, sent_feats)
        elif mode == '-test':
            test_file = sys.argv[3]
            sent_parser_model = sys.argv[4]
            output_file = sys.argv[5]
            test(test_file, None, sent_parser_model, output_file, None, sent_feats)


    elif flag.startswith('-fa'):
        sent_feats = 'ab'+flag[3]
        if mode == '-train':
            train_file = sys.argv[3]
            sent_parser_model = sys.argv[4]
            train(train_file, None, sent_parser_model, None, sent_feats)
        elif mode == '-test':
            test_file = sys.argv[3]
            sent_parser_model = sys.argv[4]
            output_file = sys.argv[5]
            test(test_file, None, sent_parser_model, output_file, None, sent_feats)



    elif flag == '-chunk' or flag == '-clause':
        unit_feats = 'a'
        sent_feats = 'ad'
        if mode == '-train':    
            train_file = sys.argv[3]
            unit_parser_model = sys.argv[4]
            sent_parser_model = sys.argv[5]
            train(train_file, unit_parser_model, sent_parser_model, unit_feats, sent_feats, flag)
        elif mode == '-test':
            test_file = sys.argv[3]
            unit_parser_model = sys.argv[4]
            sent_parser_model = sys.argv[5]
            output_file = sys.argv[6]
            factor = sys.argv[7]
            test(test_file, unit_parser_model, sent_parser_model, output_file, unit_feats, sent_feats, flag, float(factor))


    elif flag == '-chunk-feat' or flag == '-clause-feat':
        if flag == '-chunk-feat':
            flag = '-chunk'
        else:
            flag = '-clause'
        unit_feats = 'a'
        sent_feats = 'ac'
        if mode == '-train':    
            train_file = sys.argv[3]
            unit_parser_model = sys.argv[4]
            sent_parser_model = sys.argv[5]
            train(train_file, unit_parser_model, sent_parser_model, unit_feats, sent_feats, flag)
        elif mode == '-test':
            test_file = sys.argv[3]
            unit_parser_model = sys.argv[4]
            sent_parser_model = sys.argv[5]
            output_file = sys.argv[6]
            test(test_file, unit_parser_model, sent_parser_model, output_file, unit_feats, sent_feats, flag)




