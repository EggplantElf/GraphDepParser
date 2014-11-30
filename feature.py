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



def make_unigram_features(sent, unit = []):
    # features are triples like ('took', 'VB', 'past')
    if unit:
        return [(sent[i].form, sent[i].pos) for i in unit + [0]]
    else:
        return [(sent[i].form, sent[i].pos) for i in xrange(len(sent))]



def make_features_for_parser(sent, unigrams, h, d, map_func, feats):
    features = []

    hform, hpos = unigrams[h]
    dform, dpos = unigrams[d]  


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

    # # what does ancestor() do? get the head of each chunk as a representation of the chunk
    # # might make a difference while parsing with chunk information
    # h01pos = unigrams[ancestor(sent, h-1)][1] if h >= 1 else '<NA>'
    # h02pos = unigrams[ancestor(sent, h-2)][1] if h >= 2 else '<NA>'
    # h11pos = unigrams[ancestor(sent, h+1)][1] if h + 1 < len(sent) else '<NA>'
    # h12pos = unigrams[ancestor(sent, h+2)][1] if h + 2 < len(sent) else '<NA>'
    # d01pos = unigrams[ancestor(sent, d-1)][1] if d >= 1 else '<NA>'
    # d02pos = unigrams[ancestor(sent, d-2)][1] if d >= 2 else '<NA>'
    # d11pos = unigrams[ancestor(sent, d+1)][1] if d + 1 < len(sent) else '<NA>'
    # d12pos = unigrams[ancestor(sent, d+2)][1] if d + 2 < len(sent) else '<NA>'

    offset = h - d
    flag = '%d~' % offset
    if -4 < offset < 4:
        flag = '1s~%d~' % offset
    else:
        flag = '4s~%d~' % (offset / 4 * 4)

    # if h > d:
    #     fg = 'h>d~'
    # else:
    #     fg = 'h<d~'

    if offset > 0:
        if offset == 1:
            frog = '+0s~'
        else:
            frog = '+1s~'
    else:
        if offset == -1:
            frog = '-0s~'
        else:
            frog = '-1s~'


    # a) 
    features.append(map_func('$a~' + frog + 'h.form~h.pos:%s~%s' % (hform, hpos)))
    features.append(map_func('$b~' + frog + 'h.form:%s' % (hform)))
    features.append(map_func('$c~' + frog + 'h.h.pos:%s' % (hpos)))

    features.append(map_func('$d~' + frog + 'd.form~d.pos:%s~%s' % (dform, dpos)))
    features.append(map_func('$e~' + frog + 'd.form:%s' % (dform)))
    features.append(map_func('$f~' + frog + 'd.d.pos:%s' % (dpos)))

    # b)
    # what about 5-gram prefix?
    features.append(map_func('$g~' + frog + 'h.form~h.pos~d.form~d.pos:%s~%s~%s~%s' % (hform, hpos, dform, dpos)))
    features.append(map_func('$h~' + frog + 'h.pos~d.form~d.pos:%s~%s~%s' % (hpos, dform, dpos)))
    features.append(map_func('$i~' + frog + 'h.form~d.form~d.pos:%s~%s~%s' % (hform, dform, dpos)))
    features.append(map_func('$j~' + frog + 'h.form~h.pos~d.pos:%s~%s~%s' % (hform, hpos, dpos)))
    features.append(map_func('$k~' + frog + 'h.form~h.pos~d.form:%s~%s~%s' % (hform, hpos, dform)))
    features.append(map_func('$l~' + frog + 'h.form~d.form:%s~%s' % (hform, dform)))
    features.append(map_func('$m~' + frog + 'h.pos~d.pos:%s~%s' % (hpos, dpos)))
    features.append(map_func('$n~' + frog + 'h.pos~d.form:%s~%s' % (hpos, dform)))
    features.append(map_func('$o~' + frog + 'h.form~d.pos:%s~%s' % (hform, dpos)))




    # c)
    # strange in between pos

    for b in range(min(h, d) + 1, max(h, d)):
        bpos = unigrams[b][1]
        features.append(map_func('$p~' + frog + 'h.pos~b.pos~d.pos:%s~%s~%s' % (hpos, bpos, dpos)))

    features.append(map_func('$q~' + frog + 'all-b.pos:%s' % '~'.join(map(lambda x: unigrams[x][1], range(min(h, d), max(h, d) + 1)))))


    features.append(map_func('$r~' + frog + 'h~h+1~d~d-1:%s~%s~%s~%s' % (hpos, h11pos, dpos, d01pos)))
    features.append(map_func('$s~' + frog + 'h~h-1~d~d+1:%s~%s~%s~%s' % (hpos, h01pos, dpos, d11pos)))
    features.append(map_func('$t~' + frog + 'h~h+1~d~d+1:%s~%s~%s~%s' % (hpos, h11pos, dpos, d11pos)))
    features.append(map_func('$u~' + frog + 'h~h-1~d~d-1:%s~%s~%s~%s' % (hpos, h01pos, dpos, d01pos)))

    # d) new 
    features.append(map_func('$v~' + frog + 'h~d~d-1~d-2:%s~%s~%s~%s' % (hpos, dpos, d01pos, d02pos)))
    features.append(map_func('$w~' + frog + 'h~d~d+1~d+2:%s~%s~%s~%s' % (hpos, dpos, d11pos, d12pos)))
    features.append(map_func('$x~' + frog + 'h~d+1~d~d-1:%s~%s~%s~%s' % (hpos, d11pos, dpos, d01pos)))
    features.append(map_func('$y~' + frog + 'h-1~h~h+1~d:%s~%s~%s~%s' % (h01pos, hpos, h11pos, dpos)))
    features.append(map_func('$z~' + frog + 'h.pos~d.form:%s~%s' % (hpos, dform)))
    features.append(map_func('$A~' + frog + 'h.form~d.pos:%s~%s' % (hpos, dpos)))





    # features.append(map_func(flag + 'h.pos~d.pos:%s~%s' % (hpos, dpos)))
    # features.append(map_func(flag + 'h.pos~d.form:%s~%s' % (hpos, dform)))
    # features.append(map_func(flag + 'h.form~d.pos:%s~%s' % (hform, dpos)))
    # features.append(map_func(flag + 'h.form~d.form:%s~%s' % (hform, dform)))

    # features.append(map_func(flag + 'h~h+1~d~d+1:%s~%s~%s~%s' % (hpos, h11pos, dpos, d11pos)))
    # features.append(map_func(flag + 'h~h+1~d~d-1:%s~%s~%s~%s' % (hpos, h11pos, dpos, d01pos)))
    # features.append(map_func(flag + 'h~h-1~d~d+1:%s~%s~%s~%s' % (hpos, h01pos, dpos, d11pos)))
    # features.append(map_func(flag + 'h~h-1~d~d-1:%s~%s~%s~%s' % (hpos, h01pos, dpos, d01pos)))
    # features.append(map_func(flag + 'h~h+1~h+2~d:%s~%s~%s~%s' % (hpos, h11pos, h12pos, dpos))) #new
    # features.append(map_func(flag + 'h~h-1~h-2~d:%s~%s~%s~%s' % (hpos, h01pos, h02pos, dpos))) #new
    # features.append(map_func(flag + 'h~d~d+1~d+2:%s~%s~%s~%s' % (hpos, dpos, d11pos, d12pos)))
    # features.append(map_func(flag + 'h~d~d-1~d-2:%s~%s~%s~%s' % (hpos, dpos, d01pos, d02pos)))
    # features.append(map_func(flag + 'h~d+1~d~d-1:%s~%s~%s~%s' % (hpos, d11pos, dpos, d01pos)))
    # features.append(map_func(flag + 'h+1~h~h-1~d:%s~%s~%s~%s' % (h11pos, hpos, h01pos, dpos)))





    # if h < d:
        # features.append(map_func(flag + 'b.pos:%s' % '~'.join(map(lambda x: unigrams[x][1], range(h, d+1)))))
    # else:
    #     features.append(map_func(flag + 'b.pos:%s' % '~'.join(map(lambda x: unigrams[x][1], range(d, h+1)))))
    # # # features.append(map_func('h<d~between.pos~mor:%s' % '~'.join(map(lambda x: '%s~%s' % (sent[x].pos, sent[x].mor), range(h, d+1)))))
    # # # features.append(map_func('d<h~between.pos~mor:%s' % '~'.join(map(lambda x: '%s~%s' % (sent[x].pos, sent[x].mor), range(d, h+1)))))

    # # # morph

    # # too simple, need change! 
    # # use some second order features from the unit parsing
    # # while finding head for the head of a unit, its children are the second order features



    if 'b' in feats:
        features.append(map_func(flag + 'ctag:%s~%s' % (sent[h].ctag, sent[d].ctag)))
        features.append(map_func(flag + 'ctag~hpos~dpos:%s~%s~%s~%s' % (sent[h].ctag, sent[d].ctag, hpos, dpos)))



    if 'c' in feats:
        deps = all_deps(sent)
        if sent[d].unithead:
            if sent[d].unithead == h:
                unit_flag = 'same~'
            else:
                unit_flag = 'diff~'
        else:
            unit_flag = 'nohead~'

        hld = left_dep(deps, h)
        hrd = right_dep(deps, h)
        dld = left_dep(deps, d)
        drd = right_dep(deps, d)
        hldpos = unigrams[hld][1] if hld else '<NA>'
        hrdpos = unigrams[hrd][1] if hrd else '<NA>'
        dldpos = unigrams[dld][1] if dld else '<NA>'
        drdpos = unigrams[drd][1] if drd else '<NA>'

        features.append(map_func(frog + unit_flag))
        features.append(map_func(frog + unit_flag + 'h~d~%s~%s' % (hpos, dpos)))
        features.append(map_func(frog + unit_flag + 'h~dld~drd~%s~%s~%s' % (hpos, dldpos, drdpos)))
        features.append(map_func(frog + unit_flag + 'd~hld~hrd~%s~%s~%s' % (dpos, hldpos, hrdpos)))
        features.append(map_func(frog + unit_flag + 'hld~hrd~dld~drd~%s~%s~%s~%s' % (hldpos, hrdpos, dldpos, drdpos)))
        features.append(map_func(frog + unit_flag + 'h~d~hld~hrd~dld~drd~%s~%s~%s~%s~%s~%s' % (hpos, dpos, hldpos, hrdpos, dldpos, drdpos)))

    return filter(None, features)


def all_deps(sent):
    deps = {}
    for d in range(1, len(sent)):
        h = sent[d].unithead
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
    a = sent[d].unithead
    while a:
        d = a 
        a = sent[d].unithead
    return d




