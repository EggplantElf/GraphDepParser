def make_features_for_labeler(sent, h, d, map_func):
    features = []

    nodes = range(1, len(sent))
    hpos, hform, hmor = sent[h].pos, sent[h].form, sent[h].mor
    dpos, dform, dmor = sent[d].pos, sent[d].form, sent[d].mor
    h01pos = (h != 0 and h-1 in nodes) and sent[h-1].pos or '<NA>'
    h02pos = (h != 0 and h-2 in nodes) and sent[h-2].pos or '<NA>'
    h11pos = (h != 0 and h+1 in nodes) and sent[h+1].pos or '<NA>'
    h12pos = (h != 0 and h+2 in nodes) and sent[h+2].pos or '<NA>'


    d01pos = (d != 0 and d-1 in nodes) and sent[d-1].pos or '<NA>'
    d02pos = (d != 0 and d-2 in nodes) and sent[d-2].pos or '<NA>'
    d11pos = (d != 0 and d+1 in nodes) and sent[d+1].pos or '<NA>'
    d12pos = (d != 0 and d+2 in nodes) and sent[d+2].pos or '<NA>'

    if h < d:
        features.append(map_func('h.pos~d.pos:%s~%s' % (hpos, dpos)))
        features.append(map_func('h.pos~d.form:%s~%s' % (hpos, dform)))
        features.append(map_func('h.form~d.pos:%s~%s' % (hform, dpos)))
        # features.append(map_func('h.form~d.form:%s~%s' % (hform, dform)))
        features.append(map_func('h.mor~d.mor:%s~%s' % (hmor, dmor)))
        features.append(map_func('h.mor~h.pos~d.mor~d.pos:%s~%s~%s~%s' % (hmor, hpos, dmor, dpos)))

    else:
        features.append(map_func('d.pos~h.pos:%s~%s' % (dpos, hpos)))
        features.append(map_func('d.pos~h.form:%s~%s' % (dpos, hform)))
        features.append(map_func('d.form~h.pos:%s~%s' % (dform, hpos)))
        # features.append(map_func('d.form~h.form:%s~%s' % (dform, hform)))
        features.append(map_func('d.mor~h.mor:%s~%s' % (dmor, hmor)))
        features.append(map_func('d.mor~d.pos~h.mor~h.pos:%s~%s~%s~%s' % (dmor, dpos, hmor, hpos)))



    return filter(None, features)




def make_features_for_parser(sent, h, d, map_func):
    features = []

    nodes = range(1, len(sent))
    hpos, hform, hmor = sent[h].pos, sent[h].form, sent[h].mor
    dpos, dform, dmor = sent[d].pos, sent[d].form, sent[d].mor
    h01pos = (h != 0 and h-1 in nodes) and sent[h-1].pos or '<NA>'
    h02pos = (h != 0 and h-2 in nodes) and sent[h-2].pos or '<NA>'
    h11pos = (h != 0 and h+1 in nodes) and sent[h+1].pos or '<NA>'
    h12pos = (h != 0 and h+2 in nodes) and sent[h+2].pos or '<NA>'


    d01pos = (d != 0 and d-1 in nodes) and sent[d-1].pos or '<NA>'
    d02pos = (d != 0 and d-2 in nodes) and sent[d-2].pos or '<NA>'
    d11pos = (d != 0 and d+1 in nodes) and sent[d+1].pos or '<NA>'
    d12pos = (d != 0 and d+2 in nodes) and sent[d+2].pos or '<NA>'


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
    if offset < 10 and offset > -10:
        features.append(map_func('1step_offset:%d' % offset))
    else:
        features.append(map_func('4step_offset:%d' % (offset / 4 * 4)))




    # # features.append(map_func('offset:%d' % (h - d)))
    features.append(map_func('h<d~b.pos:%s' % '~'.join(map(lambda x: sent[x].pos, range(h, d+1)))))
    features.append(map_func('d<h~b.pos:%s' % '~'.join(map(lambda x: sent[x].pos, range(d, h+1)))))
    # # features.append(map_func('h<d~between.pos~mor:%s' % '~'.join(map(lambda x: '%s~%s' % (sent[x].pos, sent[x].mor), range(h, d+1)))))
    # # features.append(map_func('d<h~between.pos~mor:%s' % '~'.join(map(lambda x: '%s~%s' % (sent[x].pos, sent[x].mor), range(d, h+1)))))

    # # morph




    if h < d:
        bpos = map(lambda x: '%s~%s' % (sent[x].pos, sent[x].mor), range(h+1, d))        
    else:
        bpos = map(lambda x: '%s~%s' % (sent[x].pos, sent[x].mor), range(d+1, h))

    # for pos in bpos:
    #     f = 'b.pos~mor:%s' % pos
    #     if f not in features:
    #         features.append(map_func(f))
    for pos in bpos:
        if h < d:
            f = 'h.pos~b.pos~d.pos:%s~%s~%s' % (hpos, bpos, dpos)
        else:
            f = 'd.pos~b.pos~h.pos:%s~%s~%s' % (dpos, bpos, hpos)

        if f not in features:
            features.append(map_func(f))


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


def make_features_for_easy_parser(sent, h, d, map_func):
    features = []

    nodes = range(1, len(sent))
    hpos, hform, hmor = sent[h].pos, sent[h].form, sent[h].mor
    dpos, dform, dmor = sent[d].pos, sent[d].form, sent[d].mor
    h01pos = (h != 0 and h-1 in nodes) and sent[h-1].pos or '<NA>'
    h02pos = (h != 0 and h-2 in nodes) and sent[h-2].pos or '<NA>'
    h11pos = (h != 0 and h+1 in nodes) and sent[h+1].pos or '<NA>'
    h12pos = (h != 0 and h+2 in nodes) and sent[h+2].pos or '<NA>'


    d01pos = (d != 0 and d-1 in nodes) and sent[d-1].pos or '<NA>'
    d02pos = (d != 0 and d-2 in nodes) and sent[d-2].pos or '<NA>'
    d11pos = (d != 0 and d+1 in nodes) and sent[d+1].pos or '<NA>'
    d12pos = (d != 0 and d+2 in nodes) and sent[d+2].pos or '<NA>'

    if h < d:
        features.append(map_func('h.pos~d.pos:%s~%s' % (hpos, dpos)))
        features.append(map_func('h.pos~d.form:%s~%s' % (hpos, dform)))
        features.append(map_func('h.form~d.pos:%s~%s' % (hform, dpos)))
        # features.append(map_func('h.form~d.form:%s~%s' % (hform, dform)))
        # features.append(map_func('h.mor~d.mor:%s~%s' % (hmor, dmor)))
        # features.append(map_func('h.mor~h.pos~d.mor~d.pos:%s~%s~%s~%s' % (hmor, hpos, dmor, dpos)))

    else:
        features.append(map_func('d.pos~h.pos:%s~%s' % (dpos, hpos)))
        features.append(map_func('d.pos~h.form:%s~%s' % (dpos, hform)))
        features.append(map_func('d.form~h.pos:%s~%s' % (dform, hpos)))
        # features.append(map_func('d.form~h.form:%s~%s' % (dform, hform)))
        # features.append(map_func('d.mor~h.mor:%s~%s' % (dmor, hmor)))
        # features.append(map_func('d.mor~d.pos~h.mor~h.pos:%s~%s~%s~%s' % (dmor, dpos, hmor, hpos)))



    return filter(None, features)

