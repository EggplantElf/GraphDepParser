
gold='../data/english/dev/wsj_dev.conll06'
train_file='../tmp/wsj_train.cx'
test_file='../tmp/wsj_dev.cx'

sent_parser='../tmp/sent.parser'
IOB_sent_parser='../tmp/sent.parser'
chunk_parser='../tmp/chunk.parser'
clause_parser='../tmp/clause.parser'
chunk_sent_parser='../tmp/chunk_sent.parser'
clause_sent_parser='../tmp/clause_sent.parser'



baseline_output='../tmp/wsj_dev.pred.baseline.conll06'
IOB_output='../tmp/wsj_dev.pred.IOB.conll06'
chunk_output='../tmp/wsj_dev.pred.chunk.conll06'
clause_output='../tmp/wsj_dev.pred.clause.conll06'



# baseline
python chunk_parser_main.py -baseline -train $train_file $sent_parser
python chunk_parser_main.py -baseline -test $test_file $sent_parser $baseline_output

# baseline + IOB feature
python chunk_parser_main.py -IOB -train $train_file $IOB_sent_parser
python chunk_parser_main.py -IOB -test $test_file $IOB_sent_parser $IOB_output


# parse chunk
python chunk_parser_main.py -chunk -train $train_file $chunk_parser $chunk_sent_parser 
for f in 1.1 1.2 1.3 1.5 2 3 5
do
    echo ../tmp/chunk_output.$f.conll06
    python chunk_parser_main.py -chunk -test $test_file $chunk_parser $chunk_sent_parser ../tmp/chunk_output.$f.conll06 $f
done

# parse clause
python chunk_parser_main.py -clause -train $train_file $clause_parser $clause_sent_parser 
for f in 1.1 1.2 1.3 1.5 2 3 5
do
    echo ../tmp/clause_output.$f.conll06
    python chunk_parser_main.py -clause -test $test_file $clause_parser $clause_sent_parser ../tmp/clause_output.$f.conll06 $f
done

# results
echo baseline
perl eval07.pl -q  -g $gold -s $baseline_output

echo IOB
perl eval07.pl -q  -g $gold -s $IOB_output

for f in 1.1 1.2 1.3 1.5 2 3 5
do
    echo ../tmp/chunk_output.$f.conll06
    perl eval07.pl -q  -g $gold -s ../tmp/chunk_output.$f.conll06  
done

for f in 1.1 1.2 1.3 1.5 2 3 5
do
    echo ../tmp/clause_output.$f.conll06
    perl eval07.pl -q  -g $gold -s ../tmp/clause_output.$f.conll06  
done

