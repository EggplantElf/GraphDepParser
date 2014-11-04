from itertools import imap

def make_features_for_labeler(sent, unigrams, h, d, map_func):
    features = []

    hform, hpos, hmor = unigrams[h]
    dform, dpos, dmor = unigrams[d]  
    dds = deps(sent, d)
    ddforms = '+'.join([sent[d].form for d in dds])
    ddpos = '+'.join([sent[d].pos for d in dds])

    if h < d:
        features.append(map_func('h.pos~d.pos:%s~%s' % (hpos, dpos)))
        features.append(map_func('h.pos~d.form:%s~%s' % (hpos, dform)))
        features.append(map_func('h.form~d.pos:%s~%s' % (hform, dpos)))
        # features.append(map_func('h.form~d.form:%s~%s' % (hform, dform)))
        features.append(map_func('h.mor~d.mor:%s~%s' % (hmor, dmor)))
        features.append(map_func('h.mor~h.pos~d.mor~d.pos:%s~%s~%s~%s' % (hmor, hpos, dmor, dpos)))
        features.append(map_func('h.pos~dd.form:%s~%s' % (hpos, ddforms))) #new
        features.append(map_func('h.pos~dd.pos:%s~%s' % (hpos, ddpos))) #new
        features.append(map_func('h.form~dd.pos:%s~%s' % (hform, ddpos))) #new


    else:
        features.append(map_func('d.pos~h.pos:%s~%s' % (dpos, hpos)))
        features.append(map_func('d.pos~h.form:%s~%s' % (dpos, hform)))
        features.append(map_func('d.form~h.pos:%s~%s' % (dform, hpos)))
        # features.append(map_func('d.form~h.form:%s~%s' % (dform, hform)))
        features.append(map_func('d.mor~h.mor:%s~%s' % (dmor, hmor)))
        features.append(map_func('d.mor~d.pos~h.mor~h.pos:%s~%s~%s~%s' % (dmor, dpos, hmor, hpos)))
        features.append(map_func('dd.form~h.pos:%s~%s' % (ddforms, hpos))) #new
        features.append(map_func('dd.pos~h.pos:%s~%s' % (ddpos, hpos))) #new



    return filter(None, features)



def deps(sent, h):
    return [d for d in range(1, len(sent)) if sent[d].head == h]



def make_unigram_features(sent, chunk = []):
    # features are triples like ('took', 'VB', 'past')
    if chunk:
        return [(sent[i].form, sent[i].pos, sent[i].mor) for i in chunk + [0]]
    else:
        return [(sent[i].form, sent[i].pos, sent[i].mor) for i in xrange(len(sent))]



def make_features_for_parser(sent, unigrams, h, d, map_func, chunks = [], chunk_info = False):
    features = []

    hform, hpos, hmor = unigrams[h]
    dform, dpos, dmor = unigrams[d]  
    h01pos = unigrams[h-1][1] if h >= 1 else '<NA>'
    h02pos = unigrams[h-2][1] if h >= 2 else '<NA>'
    h11pos = unigrams[h+1][1] if h + 1 < len(sent) else '<NA>'
    h12pos = unigrams[h+2][1] if h + 2 < len(sent) else '<NA>'
    # there was a stupid mistake! 
    # yet another!
    d01pos = unigrams[d-1][1] if d >= 1 else '<NA>'
    d02pos = unigrams[d-2][1] if d >= 2 else '<NA>'
    d11pos = unigrams[d+1][1] if d + 1 < len(sent) else '<NA>'
    d12pos = unigrams[d+2][1] if d + 2 < len(sent) else '<NA>'


    # h01pos = unigrams[ancestor(sent, h-1)][1] if h >= 1 else '<NA>'
    # h02pos = unigrams[ancestor(sent, h-2)][1] if h >= 2 else '<NA>'
    # h11pos = unigrams[ancestor(sent, h+1)][1] if h + 1 < len(sent) else '<NA>'
    # h12pos = unigrams[ancestor(sent, h+2)][1] if h + 2 < len(sent) else '<NA>'
    # d01pos = unigrams[ancestor(sent, d-1)][1] if d >= 1 else '<NA>'
    # d02pos = unigrams[ancestor(sent, d-2)][1] if d >= 2 else '<NA>'
    # d11pos = unigrams[ancestor(sent, d+1)][1] if d + 1 < len(sent) else '<NA>'
    # d12pos = unigrams[ancestor(sent, d+2)][1] if d + 2 < len(sent) else '<NA>'



    if h < d:
        flag = 'h<d~'
    else:
        flag = 'h>d~'

    if h < d:
        features.append(map_func('h.pos~d.pos:%s~%s' % (hpos, dpos)))
        features.append(map_func('h.pos~d.form:%s~%s' % (hpos, dform)))
        features.append(map_func('h.form~d.pos:%s~%s' % (hform, dpos)))
        features.append(map_func('h.form~d.form:%s~%s' % (hform, dform)))
        features.append(map_func('h.mor~d.mor:%s~%s' % (hmor, dmor)))
        features.append(map_func('h.mor~h.pos~d.mor~d.pos:%s~%s~%s~%s' % (hmor, hpos, dmor, dpos)))

    else:
        features.append(map_func('d.pos~h.pos:%s~%s' % (dpos, hpos)))
        features.append(map_func('d.pos~h.form:%s~%s' % (dpos, hform)))
        features.append(map_func('d.form~h.pos:%s~%s' % (dform, hpos)))
        features.append(map_func('d.form~h.form:%s~%s' % (dform, hform)))
        features.append(map_func('d.mor~h.mor:%s~%s' % (dmor, hmor)))
        features.append(map_func('d.mor~d.pos~h.mor~h.pos:%s~%s~%s~%s' % (dmor, dpos, hmor, hpos)))


    if h < d:
        features.append(map_func('h~h+1~d~d+1:%s~%s~%s~%s' % (hpos, h11pos, dpos, d11pos)))
        features.append(map_func('h~h+1~d~d-1:%s~%s~%s~%s' % (hpos, h11pos, dpos, d01pos)))
        features.append(map_func('h~h-1~d~d+1:%s~%s~%s~%s' % (hpos, h01pos, dpos, d11pos)))
        features.append(map_func('h~h-1~d~d-1:%s~%s~%s~%s' % (hpos, h01pos, dpos, d01pos)))
        features.append(map_func('h~h+1~h+2~d:%s~%s~%s~%s' % (hpos, h11pos, h12pos, dpos))) #new
        features.append(map_func('h~h-1~h-2~d:%s~%s~%s~%s' % (hpos, h01pos, h02pos, dpos))) #new
        features.append(map_func('h~d~d+1~d+2:%s~%s~%s~%s' % (hpos, dpos, d11pos, d12pos)))
        features.append(map_func('h~d~d-1~d-2:%s~%s~%s~%s' % (hpos, dpos, d01pos, d02pos)))
        features.append(map_func('h~d+1~d~d-1:%s~%s~%s~%s' % (hpos, d11pos, dpos, d01pos)))
        features.append(map_func('h+1~h~h-1~d:%s~%s~%s~%s' % (h11pos, hpos, h01pos, dpos)))
    else:
        features.append(map_func('d~d+1~h~h+1:%s~%s~%s~%s' % (dpos, d11pos, hpos, h11pos)))
        features.append(map_func('d~d+1~h~h-1:%s~%s~%s~%s' % (dpos, d11pos, hpos, h01pos)))
        features.append(map_func('d~d-1~h~h+1:%s~%s~%s~%s' % (dpos, d01pos, hpos, h11pos)))
        features.append(map_func('d~d-1~h~h-1:%s~%s~%s~%s' % (dpos, d01pos, hpos, h01pos)))
        features.append(map_func('d~h~h+1~h+2:%s~%s~%s~%s' % (dpos, hpos, h11pos, h12pos))) #new
        features.append(map_func('d~h~h-1~h-2:%s~%s~%s~%s' % (dpos, hpos, h01pos, h02pos))) #new
        features.append(map_func('d~h+1~h~h-1:%s~%s~%s~%s' % (dpos, h11pos, hpos, h01pos)))
        features.append(map_func('d+1~d~d-1~h:%s~%s~%s~%s' % (d11pos, dpos, d01pos, hpos)))
        features.append(map_func('d~d+1~d+2~h:%s~%s~%s~%s' % (dpos, d11pos, d12pos, hpos)))
        features.append(map_func('d~d-1~d-2~h:%s~%s~%s~%s' % (dpos, d01pos, d02pos, hpos)))


    offset = h -d
    if -10 < offset < 10:
        features.append(map_func('1step_offset:%d' % offset))
    else:
        features.append(map_func('4step_offset:%d' % (offset / 4 * 4)))




    # # features.append(map_func('offset:%d' % (h - d)))
    features.append(map_func('h<d~b.pos:%s' % '~'.join(map(lambda x: unigrams[x][1], range(h, d+1)))))
    features.append(map_func('d<h~b.pos:%s' % '~'.join(map(lambda x: unigrams[x][1], range(d, h+1)))))
    # # features.append(map_func('h<d~between.pos~mor:%s' % '~'.join(map(lambda x: '%s~%s' % (sent[x].pos, sent[x].mor), range(h, d+1)))))
    # # features.append(map_func('d<h~between.pos~mor:%s' % '~'.join(map(lambda x: '%s~%s' % (sent[x].pos, sent[x].mor), range(d, h+1)))))

    # # morph

    # too simple, need change! 
    # use some second order features from the chunk parsing
    # while finding head for the head of a chunk, its children are the second order features




    features.append(map_func(flag + 'ctag:%s~%s' % (sent[h].ctag, sent[d].ctag)))
    features.append(map_func(flag + 'ctag~hpos~dpos:%s~%s~%s~%s' % (sent[h].ctag, sent[d].ctag, hpos, dpos)))



    if chunk_info:
        deps = all_deps(sent)
        if sent[d].chunkhead:
            if sent[d].chunkhead == h:
                chunk_flag = 'same~'
            else:
                chunk_flag = 'diff~'
        else:
            chunk_flag = 'nohead~'

        hld = left_dep(deps, h)
        hrd = right_dep(deps, h)
        dld = left_dep(deps, d)
        drd = right_dep(deps, d)
        hldpos = unigrams[hld][1] if hld else '<NA>'
        hrdpos = unigrams[hrd][1] if hrd else '<NA>'
        dldpos = unigrams[dld][1] if dld else '<NA>'
        drdpos = unigrams[drd][1] if drd else '<NA>'

        features.append(map_func(flag + chunk_flag))
        features.append(map_func(flag + chunk_flag + 'h~d~%s~%s' % (hpos, dpos)))
        features.append(map_func(flag + chunk_flag + 'h~dld~drd~%s~%s~%s' % (hpos, dldpos, drdpos)))
        features.append(map_func(flag + chunk_flag + 'd~hld~hrd~%s~%s~%s' % (dpos, hldpos, hrdpos)))
        features.append(map_func(flag + chunk_flag + 'hld~hrd~dld~drd~%s~%s~%s~%s' % (hldpos, hrdpos, dldpos, drdpos)))
        features.append(map_func(flag + chunk_flag + 'h~d~hld~hrd~dld~drd~%s~%s~%s~%s~%s~%s' % (hpos, dpos, hldpos, hrdpos, dldpos, drdpos)))



        # if h in deps:


        # if sent[d].chunkhead:

        #     if sent[d].chunkhead == h:
        #         # features.append(map_func(flag + 'head_is_chunkhead'))
        #         features.append(map_func(flag + 'head_is_chunkhead~h.pos~d.pos:%s~%s' % (hpos, dpos)))


        # #         features.append(map_func(flag + 'head_is_not_chunkhead'))
        # #         features.append(map_func(flag + 'head_is_not_chunkhead~h.pos~d.pos:%s~%s' % (hpos, dpos)))
        # # else:
        # #     features.append(map_func(flag + 'head_not_in_chunk'))

    return filter(None, features)


def all_deps(sent):
    deps = {}
    for d in range(1, len(sent)):
        h = sent[d].chunkhead
        if h:
            if h not in deps:
                deps[h] = [d]
            else:
                deps[h].append(d)
    return deps


def left_dep(deps, h):
    if h in deps and deps[h][0] < h:
        return deps[h][0]

def right_dep(deps, h):
    if h in deps and deps[h][-1] > h:
        return deps[h][-1]


def ancestor(sent, d):
    a = sent[d].chunkhead
    while a:
        d = a 
        a = sent[d].chunkhead
    return d




