from __future__ import division
import sys


def stat(cx_file):
    chunk_stat = {}
    clause_stat = {}
    phrase_stat = {}
    total = 0
    total_chunk = 0
    total_clause = 0
    wrong_chunk = 0
    wrong_clause = 0
    for sent in read_sentences(cx_file):
        total += 1
        chunks = get_chunks(sent)
        clauses = get_clauses(sent)
        total_chunk += len(chunks)
        total_clause += len(clauses)
        for chunk in chunks:
            l = len(chunk)
            if l not in chunk_stat:
                chunk_stat[l] = 1 
            else:
                chunk_stat[l] += 1
            p = chunk[0][0].split('-')[1]
            if p not in phrase_stat:
                phrase_stat[p] = {}
            if l not in phrase_stat[p]:
                phrase_stat[p][l] = 1
            else:
                phrase_stat[p][l] += 1

            if not check(chunk):
                wrong_chunk += 1
                for w in chunk:
                    print w
                print '-' * 20
                print 

        for clause in clauses:
            l = len(clause)
            if l not in clause_stat:
                clause_stat[l] = 1 
            else:
                clause_stat[l] += 1

            if not check(clause):
                wrong_clause += 1


    print 'total sents:', total

    print sum(clause_stat.values()), clause_stat

    for p in sorted(phrase_stat.keys(), key = lambda x: sum(phrase_stat[x].values()), reverse = True):
        print p, '&', sum(phrase_stat[p].values()), '&', 
        s = 0
        for i in range(1,5):
            if i in phrase_stat[p]:
                s += phrase_stat[p][i] / sum(phrase_stat[p].values()) * 100
                print '%.1f\\%% &' % (phrase_stat[p][i] / sum(phrase_stat[p].values()) * 100),
            else:
                print '0.0\\% &',
        print '%.1f\\\\' % (100 - s)

    for c in clause_stat:
        print c , '%.4f' % (clause_stat[c] / sum(clause_stat.values()) * 100)


    for p in sorted(phrase_stat.keys(), key = lambda x: sum(phrase_stat[x].values()), reverse = True):
        print p, '\t', sum(phrase_stat[p].values()),  '\t',
        s = 0
        for i in range(1,5):
            if i in phrase_stat[p]:
                s += phrase_stat[p][i]
                print phrase_stat[p][i], '\t',
            else:
                print '0\t',
        print sum(phrase_stat[p].values()) - s

    print 'total chunk:', total_chunk
    print 'wrong chunk:', wrong_chunk
    print 'total clause:', total_clause
    print 'wrong clause:', wrong_clause


def read_sentences(cx_file):
    sent = [('', -1)]
    for line in open(cx_file):
        line = line.strip()
        if line:
            items = line.split()
            ctag = items[10]
            tid = int(items[0])
            hid = int(items[6])
            word = items[1]
            sent.append((ctag, tid, hid, word))
        else:
            yield sent
            sent = [('', -1)]



def get_chunks(sent):
    chunks = []
    chunk = []
    for (ctag, tid, hid, word) in sent[1:]:
        if ctag[0] in ['B', 'O']:
            if chunk:
                chunks.append(chunk)
            chunk = [(ctag, tid, hid, word)]
        else:
            chunk.append((ctag, tid, hid, word))
    chunks.append(chunk)
    return filter(lambda x: x[0][0] != 'O', chunks)

def get_clauses(sent):
    clauses = []
    clause = []
    for (ctag, tid, hid, word) in sent[1:]:
        if ctag[0] == 'O':
            if clause:
                clauses.append(clause)
            clause = []
        else:
            clause.append((ctag, tid, hid, word))
    return clauses

def check(unit):
    tids = [tid for (ctag, tid, hid, word) in unit]
    hids = [hid for (ctag, tid, hid, word) in unit]
    return len([h for h in hids if h not in tids]) == 1



if __name__ == '__main__':
    stat(sys.argv[1])
