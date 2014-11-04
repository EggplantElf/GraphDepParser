
evalscript='../data/english/dev/wsj_dev.conll06'
train_file='../tmp/wsj_train.cx'
test_file='../tmp/wsj_dev.cx'
baseline_output='../tmp/wsj_dev.pred.baseline.conll06'
IOB_output='../tmp/wsj_dev.pred.IOB.conll06'
chunk_parser='../tmp/chunk.parser'
clause_parser='../tmp/clause.parser'
sent_parser='../tmp/sent.parser'



# baseline
python chunk_parser_main.py -baseline $train_file $sent_parser $test_file $baseline_output

# baseline + IOB feature
python chunk_parser_main.py -IOB $train_file $sent_parser $test_file $IOB_output



perl eval07.pl -q  -g $evalscript -s $baseline_output
perl eval07.pl -q  -g $evalscript -s $IOB_output
