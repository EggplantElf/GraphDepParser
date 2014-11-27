import sys
from model import *


def show_weights(model_file,  filter_func = None):
    model = ParserModel(model_file)
    features = {}
    for f in model.featmap:
        if not filter_func or filter_func(model.featmap[f]):
            print '%s\t%6.2f' % (f, model.weights[model.featmap[f]-1])

        if f[:2] not in features:
            features[f[:2]] = 1
        else:
            features[f[:2]] += 1

    for f in sorted(features.keys()):
        print f,'\t', features[f]





if __name__ == '__main__':
    show_weights(sys.argv[1])