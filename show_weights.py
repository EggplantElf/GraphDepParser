import sys
from parser import *

def show_weights(model_file, filter_func = None):
    model = Model(model_file)
    for f in model.featmap:
        if not filter_func or filter_func(model.featmap[f]):
            print '%s\t%6.2f' % (f, model.weights[model.featmap[f]-1])


if __name__ == '__main__':
    show_weights(sys.argv[1])