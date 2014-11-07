
gold='../data/english/dev/wsj_dev.conll06'
train_file='../tmp/wsj_train.cx'
test_file='../tmp/wsj_dev.cx'

sent_parser='../tmp/sent.parser'
IOB_sent_parser='../tmp/sent.parser'
chunk_parser='../tmp/chunk.parser'
clause_parser='../tmp/clause.parser'
chunk_sent_parser = '../tmp/chunk_sent.parser'
clause_sent_parser = '../tmp/clause_sent.parser'



baseline_output='../tmp/wsj_dev.pred.baseline.conll06'
IOB_output='../tmp/wsj_dev.pred.IOB.conll06'
chunk_output='../tmp/wsj_dev.pred.chunk.conll06'
clause_output='../tmp/wsj_dev.pred.clause.conll06'

factor='1.2'


# baseline
python chunk_parser_main.py -baseline -train $train_file $sent_parser
python chunk_parser_main.py -baseline -test $test_file $sent_parser $baseline_output

# baseline + IOB feature
python chunk_parser_main.py -IOB -train $train_file $IOB_sent_parser
python chunk_parser_main.py -IOB -test $test_file $IOB_sent_parser $IOB_output


# parse chunk
python chunk_parser_main.py -chunk -train $train_file $chunk_parser $chunk_sent_parser 
python chunk_parser_main.py -chunk -test $test_file $chunk_parser $chunk_sent_parser $chunk_output $factor


# parse clause
python chunk_parser_main.py -clause -train $train_file $clause_parser $clause_sent_parser 
python chunk_parser_main.py -clause -test $test_file $clause_parser $clause_sent_parser $clause_output $factor



perl eval07.pl -q  -g $gold -s $baseline_output
perl eval07.pl -q  -g $gold -s $IOB_output
perl eval07.pl -q  -g $gold -s $chunk_output
perl eval07.pl -q  -g $gold -s $clause_output
