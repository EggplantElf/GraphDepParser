import sys

def count(feature_file):
    features = {}
    for line in open(feature_file):
        items = line.split()
        f, w = items[0][:2], float(items[1])
        if f not in features:
            features[f] = 1
        else:
            features[f] += 1

    for f in sorted(features.keys()):
        print f, '\t', features[f]



if __name__ == '__main__':
    count(sys.argv[1])