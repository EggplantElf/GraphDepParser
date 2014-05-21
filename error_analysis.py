import sys

def analyse(conll_file):
    form_errors = {}
    edge_errors = {}
    pos_errors = {}

    sent = {0:('ROOT', 'ROOT', -1, -1)}
    i = 1
    for line in open(conll_file):
        if line.strip():
            items = line.split('\t')
            form, pos, head, phead = items[1], items[3], int(items[6]), int(items[8])
            sent[i] = (form, pos, head, phead)
            i += 1
        else:
            find_error(sent, form_errors, pos_errors, edge_errors)
            sent = {0:('ROOT', 'ROOT', -1, -1)}
            i = 1

    for key in sorted(edge_errors.keys(), key = lambda x: edge_errors[x], reverse = True)[:30]:
        print key, edge_errors[key]

    print '-----------------\n\n\n'
    for key in sorted(pos_errors.keys(), key = lambda x: pos_errors[x], reverse = True)[:30]:
        print key, pos_errors[key]


    print '-----------------\n\n\n'  
    for key in sorted(form_errors.keys(), key = lambda x: form_errors[x], reverse = True)[:100]:
        print key, form_errors[key]

def find_error(sent, form_errors, pos_errors, edge_errors):
    for i in range(1, len(sent)):
        (form, pos, head, phead) = sent[i]
        if head != phead:
            key = (pos, sent[head][1], sent[phead][1])

            if key not in edge_errors:
                edge_errors[key] = 0
            edge_errors[key] += 1

            if form not in form_errors:
                form_errors[form] = 0
            form_errors[form] += 1

            if pos not in pos_errors:
                pos_errors[pos] = 0
            pos_errors[pos] += 1            


if __name__ == '__main__':
    analyse(sys.argv[1])