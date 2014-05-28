import math, os

filtr = ['IN', 'DT', 'CC', 'TO', 'PRP', 'PRP$', 'HYPH', ',', '.']


def read(filename):
    sent = [('ROOT', -1)]
    nodes = {}
    hd_arcs = {}
    dh_arcs = {}
    for line in open(filename):
        if line.strip():
            items = line.split('\t')
            sent.append((items[1], items[3], int(items[6])))
        else:
            for tpl in sent[1:]:
                d = tpl[0]
                dp = tpl[1]
                h = sent[tpl[2]][0]
                hp = sent[tpl[2]][1]
                if h != 'ROOT':
                    if h not in hd_arcs:
                        hd_arcs[h] = {}
                    if (d, dp) not in hd_arcs[h]:
                        hd_arcs[h][(d, dp)] = 0
                    hd_arcs[h][(d, dp)] += 1

                    if d not in dh_arcs:
                        dh_arcs[d] = {}
                    if (h, hp) not in dh_arcs[d]:
                        dh_arcs[d][(h,hp)] = 0
                    dh_arcs[d][(h,hp)] += 1

            sent = [('ROOT', -1)]
    return hd_arcs, dh_arcs

def find_best_edges(hd_arcs, dh_arcs, filtr = []):
    w = raw_input('input a word\n')
    print 
    print '-' * 10
    print 'relevant deps:'
    if w in hd_arcs:
        hds = sorted(filter(lambda x: x[1] not in filtr, hd_arcs[w]), key = lambda x: hd_arcs[w][x], reverse = True)
        if len(hds) > 5:
            hds = hds[:5]
        for (w, p) in hds:
            print w, p

    print 
    print '-' * 10
    print 'relevant heads'
    if w in dh_arcs:
        dhs = sorted(filter(lambda x: x[1] not in filtr, dh_arcs[w]), key = lambda x: dh_arcs[w][x], reverse = True)
        if len(dhs) > 5:
            dhs = dhs[:5]
        for (w, p) in dhs:
            print w, p
    raw_input()
    os.system('clear')

if __name__ == '__main__':
    hd_arcs, dh_arcs =read('../data/english/train/wsj_train.conll06')
    while True:
        find_best_edges(hd_arcs, dh_arcs, filtr)
