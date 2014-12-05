
train_file='../tmp/wsj_train.gold.cx'


sent_parser='../tmp/sent.gold.parser'
IOB_sent_parser='../tmp/IOB_sent.gold.parser'
chunk_parser='../tmp/chunk.gold.parser'
clause_parser='../tmp/clause.gold.parser'
chunk_sent_parser='../tmp/chunk_sent.gold.parser'
clause_sent_parser='../tmp/clause_sent.gold.parser'

# train

# python unit_parser_main.py -baseline -train $train_file $sent_parser
# python unit_parser_main.py -IOB -train $train_file $IOB_sent_parser
# python unit_parser_main.py -chunk -train $train_file $chunk_parser $chunk_sent_parser
# python unit_parser_main.py -clause -train $train_file $clause_parser $clause_sent_parser



# test
for g in answer email newsgroup weblogs reviews
do
    test_file=../tmp/$g.cx
    baseline_output=../tmp/$g.baseline.conll06
    IOB_output=../tmp/$g.IOB.conll06
    chunk_output=../tmp/$g.chunk.conll06
    clause_output=../tmp/$g.clause.conll06
    echo $g
    # baseline
    python unit_parser_main.py -baseline -test $test_file $sent_parser $baseline_output

    # # baseline + IOB feature
    python unit_parser_main.py -IOB -test $test_file $IOB_sent_parser $IOB_output


    # parse chunk
    python unit_parser_main.py -chunk -test $test_file $chunk_parser $chunk_sent_parser $chunk_output 1.3

    # parse clause
    python unit_parser_main.py -clause -test $test_file $clause_parser $clause_sent_parser $clause_output 1.2

done



# eval
for g in answer email newsgroup weblogs reviews
do
    test_file=../tmp/$g.cx
    baseline_output=../tmp/$g.baseline.conll06
    IOB_output=../tmp/$g.IOB.conll06
    chunk_output=../tmp/$g.chunk.conll06
    clause_output=../tmp/$g.clause.conll06
    gold=../tmp/$g.conll06
    echo $g

    echo baseline
    perl eval07.pl -q -p -g $gold -s $baseline_output

    echo IOB
    perl eval07.pl -q -p -g $gold -s $IOB_output

    echo chunk_weight
    perl eval07.pl -q -p -g $gold -s $chunk_output

    echo clause_weight
    perl eval07.pl -q -p -g $gold -s $clause_output

done



