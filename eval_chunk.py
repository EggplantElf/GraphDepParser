
def evaluate(pred_file, gold_file):
    total = 0.0
    correct = 0.0

    pred = []
    gold = []
    for line in open(pred_file):
        if line.strip():
            items = line.split('\t')
            pred.append(items[6])

    for line in open(gold_file):
        if line.strip():
            items = line.split('\t')
            gold.append(items[6])


    for (p, g) in zip(pred, gold):
        if p != '0':
            if p == g:
                correct += 1
            total += 1

    print 'accuracy: %6.2f%%' % (100 * correct/total)


if __name__ == '__main__':
    evaluate('../tmp/wsj_dev.chunk.conll06', '../data/english/dev/wsj_dev.conll06')