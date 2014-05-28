import sys, os, cPickle, gzip, math, time, random
from model import *
from sentence import *
from parser import *
from labeler import *

def train(conll_file, parser_model_file, labeler_model_file):
    parser = Parser()
    labeler = Labeler()
    parser.train(conll_file, parser_model_file)
    labeler.train(conll_file, labeler_model_file)

def test(conll_file, parser_model_file, labeler_model_file, output_file):
    outstream = open(output_file,'w')
    parser = Parser(parser_model_file)
    labeler = Labeler(labeler_model_file)
    for sent in read_sentence(open(conll_file)):
        parser.predict(sent)
        labeler.predict(sent)
        print >> outstream, sent.to_str()
    outstream.close()

def evaluate(conll_file):
    total = 0.0
    correct_head = 0.0
    correct_label = 0.0
    for line in open(conll_file):
        if line.strip():
            items = line.strip().split('\t')
            total += 1
            if items[6] == items[8]:
                correct_head += 1
            if items[7] == items[9]:
                correct_label += 1
    print 'head acc: %6.2f%%' % (100 * correct_head/total)
    print 'label acc: %6.2f%%' % (100 * correct_label/total)

####################################################

if __name__ == '__main__':
    train_file = sys.argv[1]
    parser_model_file = sys.argv[2]
    labeler_model_file = sys.argv[3]
    test_file = sys.argv[4]
    output_file = sys.argv[5]
 

    t0 = time.time()
    train(train_file, parser_model_file, labeler_model_file)
    test(test_file, parser_model_file, labeler_model_file, output_file)
    evaluate(output_file)
    print 'time used:', time.time() - t0