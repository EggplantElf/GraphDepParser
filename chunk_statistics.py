import sys

def stat(cx_file):
    chunk_stat = {}
    clause_stat = {}
    phrase_stat = {}
    for sent in read_sentences(cx_file):
        chunks = get_chunks(sent)
        clauses = get_clauses(sent)
        for chunk in chunks:
            l = len(chunk)
            if l not in chunk_stat:
                chunk_stat[l] = 1 
            else:
                chunk_stat[l] += 1
            p = chunk[0].split('-')[1]
            if p not in phrase_stat:
                phrase_stat[p] = {}
            if l not in phrase_stat[p]:
                phrase_stat[p][l] = 1
            else:
                phrase_stat[p][l] += 1

        for clause in clauses:
            l = len(clause)
            if l not in clause_stat:
                clause_stat[l] = 1 
            else:
                clause_stat[l] += 1

    print sum(chunk_stat.values()), chunk_stat
    print sum(clause_stat.values()), clause_stat
    print 
    for p in phrase_stat:
        print p, sum(phrase_stat[p].values()), phrase_stat[p]

def read_sentences(cx_file):
    sent = []
    for line in open(cx_file):
        line = line.strip()
        if line:
            ctag = line.split()[10]
            sent.append(ctag)
        else:
            yield sent
            sent = []


def get_chunks(sent):
    chunks = []
    chunk = []
    for ctag in sent:
        if ctag[0] in ['B', 'O']:
            if chunk:
                chunks.append(chunk)
            chunk = [ctag]
        else:
            chunk.append(ctag)
    chunks.append(chunk)
    return filter(lambda x: x != ['O'], chunks)

def get_clauses(sent):
    clauses = []
    clause = []
    for ctag in sent:
        if ctag[0] == 'O':
            if clause:
                clauses.append(clause)
            clause = []
        else:
            clause.append(ctag)
    return clauses

if __name__ == '__main__':
    stat(sys.argv[1])
