
gold='../data/english/dev/wsj_dev.conll06'
train_file='../tmp/wsj_train.gold.cx'
test_file='../tmp/wsj_dev.gold.cx'

sent_parser='../tmp/sent.gold.parser'
IOB_sent_parser='../tmp/IOB_sent.gold.parser'
chunk_parser='../tmp/chunk.gold.parser'
clause_parser='../tmp/clause.gold.parser'
chunk_sent_parser='../tmp/chunk_sent.gold.parser'
clause_sent_parser='../tmp/clause_sent.gold.parser'
chunk_feat_parser='../tmp/chunk_feat.gold.parser'
clause_feat_parser='../tmp/clause_feat.gold.parser'


baseline_output='../tmp/wsj_dev.gold.baseline.conll06'
IOB_output='../tmp/wsj_dev.gold.IOB.conll06'
chunk_output='../tmp/wsj_dev.gold.chunk.conll06'
clause_output='../tmp/wsj_dev.gold.clause.conll06'
chunk_feat_output='../tmp/wsj_dev.gold.chunk-feat.conll06'
clause_feat_output='../tmp/wsj_dev.gold.clause-feat.conll06'



echo run_dev_gold.sh

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
    echo ../tmp/wsj_dev.chunk.gold.$f.conll06
    python unit_parser_main.py -chunk -test $test_file $chunk_parser $chunk_sent_parser ../tmp/wsj_dev.chunk.gold.$f.conll06 $f
done

# parse clause
python unit_parser_main.py -clause -train $train_file $clause_parser $clause_sent_parser 
for f in 1.1 1.2 1.3 1.5 2 3 5
do
    echo ../tmp/wsj_dev.clause.gold.$f.conll06
    python unit_parser_main.py -clause -test $test_file $clause_parser $clause_sent_parser ../tmp/wsj_dev.clause.gold.$f.conll06 $f
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
    echo ../tmp/wsj_dev.chunk.gold.$f.conll06
    perl eval07.pl -q -p -g $gold -s ../tmp/wsj_dev.chunk.gold.$f.conll06  
done

for f in 1.1 1.2 1.3 1.5 2 3 5
do
    echo ../tmp/wsj_dev.clause.gold.$f.conll06
    perl eval07.pl -q -p -g $gold -s ../tmp/wsj_dev.clause.gold.$f.conll06  
done

