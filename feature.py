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



def make_unigram_features(sent):
    # features are triples like ('took', 'VB', 'past')
    return [(sent[i].form, sent[i].pos, sent[i].mor) for i in xrange(len(sent))]


def make_features_for_parser(sent, unigrams, h, d, map_func):
    features = []

    hform, hpos, hmor = unigrams[h]
    dform, dpos, dmor = unigrams[d]  
    h01pos = unigrams[h-1][1] if h >= 1 else '<NA>'
    h02pos = unigrams[h-2][1] if h >= 2 else '<NA>'
    h11pos = unigrams[h+1][1] if h + 1 < len(sent) else '<NA>'
    h12pos = unigrams[h+1][1] if h + 2 < len(sent) else '<NA>'

    d01pos = unigrams[d-1][1] if d >= 1 else '<NA>'
    d02pos = unigrams[d-2][1] if d >= 2 else '<NA>'
    d11pos = unigrams[d+1][1] if d + 1 < len(sent) else '<NA>'
    d12pos = unigrams[d+1][1] if d + 2 < len(sent) else '<NA>'


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

    # features.append(map_func('h.pos~d.form~d.pos:%s~%s~%s' % (hpos, dform, dpos)))
    # features.append(map_func('h.form~d.form~d.pos:%s~%s~%s' % (hform, dform, dpos)))
    # features.append(map_func('h.form~h.pos~d.pos:%s~%s~%s' % (hform, hpos, dpos)))
    # features.append(map_func('h.form~h.pos~d.form:%s~%s~%s' % (hform, hpos, dform)))

    # features.append(map_func('h.form~h.pos~d.form~d.pos:%s~%s~%s~%s' % (hform, hpos, dform, dpos)))

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

    # # if h < d:
    #     # for i in range(d - h):

    # # if h < d:
    # #     for i in range(1, d - h + 1, 2):
    # #         features.append(map_func('offset:%d' % (-i)))
    # # else:
    # #     for i in range(1, h - d + 1, 2):
    # #         features.append(map_func('offset:%d' % (i)))


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



# deleted on sep. 5. (better)
    # if h < d:
    #     bpos = imap(lambda x: '%s~%s' % unigrams[x][1:], range(h+1, d))        
    # else:
    #     bpos = imap(lambda x: '%s~%s' % unigrams[x][1:], range(d+1, h))

    # # for pos in bpos:
    # #     f = 'b.pos~mor:%s' % pos
    # #     if f not in features:
    # #         features.append(map_func(f))
    # for pos in bpos:
    #     if h < d:
    #         f = 'h.pos~b.pos~d.pos:%s~%s~%s' % (hpos, bpos, dpos)
    #     else:
    #         f = 'd.pos~b.pos~h.pos:%s~%s~%s' % (dpos, bpos, hpos)

    #     if f not in features:
    #         features.append(map_func(f))


    # not helping
    # if h < d:
    #     bpos = map(lambda x: sent[x].pos, range(h, d+1))
    #     if len(bpos) > 5:
    #         bpos = bpos[:1] + bpos[-4:]

    #     features.append(map_func('h<d~between.pos:%s' % '~'.join(bpos)))
    # else:
    #     bpos = map(lambda x: sent[x].pos, range(d, h+1))
    #     if bpos > 5:
    #         bpos = bpos[:4] + bpos[-1:]
    #     features.append(map_func('d<h~between.pos:%s' % '~'.join(bpos)))

    return filter(None, features)

# structure missing
def make_features_for_easy_parser(sent, graph, h, d, map_func):
    features = []

    nodes = range(1, len(sent))
    pending = graph.pending
    if h < d:
        p = pending.index(h)
        q = pending.index(d)
        seq = 'h<d'
    else:
        p = pending.index(d)
        q = pending.index(h)
        seq = 'd<h'

    t0 = pending[p-2] if p >= 1 else None
    t1 = pending[p-1] if p >= 1 else None
    t2 = pending[p]
    t3 = pending[q]
    t4 = pending[q+1] if q + 1 < len(pending) else None
    t5 = pending[q+2] if q + 2 < len(pending) else None

    token_window = [t1, t2, t3, t4]
    pos_window = map(lambda x: sent[x].pos if x else '<NA>', token_window)
    form_window = map(lambda x: sent[x].form if x else '<NA>', token_window)
    lc_window = map(lambda x: graph.left_child(x) if x else '<NA>', token_window)
    rc_window = map(lambda x: graph.right_child(x) if x else '<NA>', token_window)


    # unigram features
    for i in xrange(len(token_window)):
        features.append(map_func('%s~%d~pos:%s' % (seq, i, pos_window[i])))
        features.append(map_func('%s~%d~form:%s' % (seq, i, form_window[i])))
        features.append(map_func('%s~%d~pos~lc:%s~%s' % (seq, i, pos_window[i], lc_window[i])))
        features.append(map_func('%s~%d~pos~rc:%s~%s' % (seq, i, pos_window[i], rc_window[i])))
        features.append(map_func('%s~%d~pos~lc~rc:%s~%s~%s' % (seq, i, pos_window[i], lc_window[i], rc_window[i])))


    # # bigram features
    # for i in xrange(len(token_window) - 1):
    #     features.append(map_func('%s~%d~ppos~qpos:%s' % (seq, i, pos_window[i], pos_window[i+1])))
    #     features.append(map_func('%s~%d~ppos~qform:%s' % (seq, i, pos_window[i], form_window[i+1])))
    #     features.append(map_func('%s~%d~pform~qpos:%s' % (seq, i, form_window[i], pos_window[i+1])))
    #     features.append(map_func('%s~%d~pform~qform:%s' % (seq, i, form_window[i], form_window[i+1])))
    #     features.append(map_func('%s~%d~ppos~qpos~plc~qlc:%s~%s~%s~%s' 
    #                             % (seq, i, pos_window[i], pos_window[i+1], lc_window[i], lc_window[i+1])))
    #     features.append(map_func('%s~%d~ppos~qpos~plc~qrc:%s~%s~%s~%s' 
    #                             % (seq, i, pos_window[i], pos_window[i+1], lc_window[i], rc_window[i+1])))
    #     features.append(map_func('%s~%d~ppos~qpos~prc~qlc:%s~%s~%s~%s' 
    #                             % (seq, i, pos_window[i], pos_window[i+1], rc_window[i], lc_window[i+1])))
    #     features.append(map_func('%s~%d~ppos~qpos~prc~qrc:%s~%s~%s~%s' 
    #                             % (seq, i, pos_window[i], pos_window[i+1], rc_window[i], rc_window[i+1])))


    # structrue features



    features.append(map_func('pending_dist:%d' % (graph.pending.index(h) - graph.pending.index(d))))
    # features.append(map_func('surface_dist:%d' % (h - d)))

    return filter(None, features)

