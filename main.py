import sys, time, argparse
from model import *
from sentence import *
from parser import *
from labeler import *
# from easy_first import *

import cProfile


def train(train_file, parser_model_file, labeler_model_file): 
    parser = Parser()
    labeler = Labeler()
    parser.train(train_file, parser_model_file)
    labeler.train(train_file, labeler_model_file)

def test(conll_file, parser_model_file, labeler_model_file, output_file):
    parser = Parser(parser_model_file)
    labeler = Labeler(labeler_model_file)
    outstream = open(output_file,'w')
    for sent in read_sentence(open(conll_file)):
        parser.predict(sent)
        labeler.predict(sent)
        print >> outstream, sent.to_str()
    outstream.close()

####################################################

if __name__ == '__main__':
    argpar = argparse.ArgumentParser(description='Parser')
    mode = argpar.add_mutually_exclusive_group(required=True)
    mode.add_argument('-train',dest='train',action='store_true',help='run in training mode')
    mode.add_argument('-test',dest='test',action='store_true',help='run in test mode')
    argpar.add_argument('-t','--trainingfile',dest='trainingfile',help='training file',required=False)
    argpar.add_argument('-p','--parser',dest='parser',help='parser model',required=True)
    argpar.add_argument('-l','--labeler',dest='labeler',help='labeler model',required=True)
    argpar.add_argument('-i','--input',dest='inputfile',help='input file',required=False)
    argpar.add_argument('-o','--output',dest='outputfile',help='output file',default='output.conll06', required=False)

    args = argpar.parse_args()

    if args.train:
        train(args.trainingfile,args.parser,args.labeler)
    elif args.test:
        test(args.inputfile, args.parser,args.labeler, args.outputfile)
