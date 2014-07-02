import sys, time
from old_model import *
from sentence import *
from parser import *
from labeler import *
# from easy_first import *

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
# import cProfile

def test(conll_file, parser, labeler, output_file):
    outstream = open(output_file,'w')
    for sent in read_sentence(open(conll_file)):
        parser.predict(sent)
        # labeler.predict(sent)
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
    print 'UAS: %6.2f%%' % (100 * correct_head/total)
    print 'LAS: %6.2f%%' % (100 * correct_label/total)

def graph_demo(argv):
    train_file = argv[1]
    parser_model_file = argv[2]
    labeler_model_file = argv[3]
    test_file = argv[4]
    output_file = argv[5]
 
    t0 = time.time()
    parser = Parser()
    # labeler = Labeler()
    parser.train(train_file, parser_model_file)
    # labeler.train(train_file, labeler_model_file)

    parser = Parser(parser_model_file)
    # labeler = Labeler(labeler_model_file)
    test(test_file, parser, None, output_file)
    evaluate(output_file)
    print 'time used:', time.time() - t0


def easy_demo(argv):
    train_file = argv[1]
    parser_model_file = argv[2]
    labeler_model_file = argv[3]
    test_file = argv[4]
    output_file = argv[5]
    max_dist = int(argv[6])

    t0 = time.time()
    parser = EasyFirstParser(max_dist = max_dist)
    parser.train(train_file, parser_model_file, 10)

    # labeler = Labeler()
    # labeler.train(train_file, labeler_model_file)

    parser = EasyFirstParser(parser_model_file, max_dist)
    labeler = Labeler(labeler_model_file)
    test(test_file, parser, labeler, output_file)
    evaluate(output_file)
    print 'time used:', time.time() - t0

####################################################

if __name__ == '__main__':
    graph_demo(sys.argv)