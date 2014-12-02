
gold='../data/english/dev/wsj_dev.conll06'
train_file='../tmp/wsj_train.fold.cx'
test_file='../tmp/wsj_dev.cx'

sent_parser='../tmp/sent.fold.parser'
IOB_sent_parser='../tmp/IOB_sent.fold.parser'
chunk_parser='../tmp/chunk.fold.parser'
clause_parser='../tmp/clause.fold.parser'
chunk_sent_parser='../tmp/chunk_sent.fold.parser'
clause_sent_parser='../tmp/clause_sent.fold.parser'
chunk_feat_parser='../tmp/chunk_feat.fold.parser'
clause_feat_parser='../tmp/clause_feat.fold.parser'


baseline_output='../tmp/wsj_dev.fold.baseline.conll06'
IOB_output='../tmp/wsj_dev.fold.IOB.conll06'
chunk_output='../tmp/wsj_dev.fold.chunk.conll06'
clause_output='../tmp/wsj_dev.fold.clause.conll06'
chunk_feat_output='../tmp/wsj_dev.fold.chunk-feat.conll06'
clause_feat_output='../tmp/wsj_dev.fold.clause-feat.conll06'



echo run_dev_fold.sh

# baseline
python unit_parser_main.py -baseline -train $train_file $sent_parser
python unit_parser_main.py -baseline -test $test_file $sent_parser $baseline_output

# baseline + IOB feature
python unit_parser_main.py -IOB -train $train_file $IOB_sent_parser
python unit_parser_main.py -IOB -test $test_file $IOB_sent_parser $IOB_output

# # chunk feat parser
# python unit_parser_main.py -chunk-feat -train $train_file $chunk_parser $chunk_feat_parser 
# python unit_parser_main.py -chunk-feat -test $test_file $chunk_parser $chunk_feat_parser $chunk_feat_output


# # clause feat parser
# python unit_parser_main.py -clause-feat -train $train_file $clause_parser $clause_feat_parser 
# python unit_parser_main.py -clause-feat -test $test_file $clause_parser $clause_feat_parser $clause_feat_output


# parse chunk
python unit_parser_main.py -chunk -train $train_file $chunk_parser $chunk_sent_parser 
for f in 1.1 1.2 1.3 1.5 2 3 5
do
    echo ../tmp/wsj_dev.chunk.fold.$f.conll06
    python unit_parser_main.py -chunk -test $test_file $chunk_parser $chunk_sent_parser ../tmp/wsj_dev.chunk.fold.$f.conll06 $f
done

# parse clause
python unit_parser_main.py -clause -train $train_file $clause_parser $clause_sent_parser 
for f in 1.1 1.2 1.3 1.5 2 3 5
do
    echo ../tmp/wsj_dev.clause.fold.$f.conll06
    python unit_parser_main.py -clause -test $test_file $clause_parser $clause_sent_parser ../tmp/wsj_dev.clause.fold.$f.conll06 $f
done

# results
echo baseline
perl eval07.pl -q -p -g $gold -s $baseline_output

echo IOB
perl eval07.pl -q -p -g $gold -s $IOB_output

# echo chunk_feat
# perl eval07.pl -q -p -g $gold -s $chunk_feat_output

# echo clause_feat
# perl eval07.pl -q -p -g $gold -s $clause_feat_output


for f in 1.1 1.2 1.3 1.5 2 3 5
do
    echo ../tmp/wsj_dev.chunk.fold.$f.conll06
    perl eval07.pl -q -p -g $gold -s ../tmp/wsj_dev.chunk.fold.$f.conll06  
done

for f in 1.1 1.2 1.3 1.5 2 3 5
do
    echo ../tmp/wsj_dev.clause.fold.$f.conll06
    perl eval07.pl -q -p -g $gold -s ../tmp/wsj_dev.clause.fold.$f.conll06  
done

