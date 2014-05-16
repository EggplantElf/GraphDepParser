import math


def read(filename):
    sent = [('ROOT', -1)]
    nodes = {}
    hd_arcs = {}
    dh_arcs = {}
    count = 0
    for line in open(filename):
        if line.strip():
            items = line.split('\t')
            sent.append((items[1], int(items[6])))
        else:
            for p in sent[1:]:
                d = p[0]
                h = sent[p[1]][0]
                if h != 'ROOT':
                    count += 1
                    if d not in nodes:
                        nodes[d] = 0
                    nodes[d] += 1

                    if h not in hd_arcs:
                        hd_arcs[h] = {}
                    if d not in hd_arcs[h]:
                        hd_arcs[h][d] = 0
                    hd_arcs[h][d] += 1

                    if d not in dh_arcs:
                        dh_arcs[d] = {}
                    if h not in dh_arcs[d]:
                        dh_arcs[d][h] = 0
                    dh_arcs[d][h] += 1

            sent = [('ROOT', -1)]
    return hd_arcs, dh_arcs




def pmi(hd_arcs, dh_arcs):
    result = []
    fh, fd = {}, {}
    for h in hd_arcs:
        fh[h] = sum([hd_arcs[h][d] for d in hd_arcs[h]])
    for d in dh_arcs:
        fd[d] = sum([dh_arcs[d][h] for h in dh_arcs[d]])
    count = sum([fh[h] for h in fh])
    for h in hd_arcs:
        for d in hd_arcs[h]:
            result.append((h, d, math.log(hd_arcs[h][d] * count * 1.0 / (fh[h] * fd[d])), hd_arcs[h][d]))
            # print '%s\t%s\t%f' % (h, d, -math.log(hd_arcs[h][d] * count * 1.0 / (fh[h] * fd[d])))
    for t in sorted(filter(lambda x: x[3] > 50, result), key = lambda x: x[2], reverse = True):
        print '%s\t%s\t%.2f\t%d' % t



if __name__ == '__main__':
    hd_arcs, dh_arcs =read('../data/english/train/wsj_train.conll06')
    pmi(hd_arcs, dh_arcs)
    # print hd_arcs
    # print dh_arcs





