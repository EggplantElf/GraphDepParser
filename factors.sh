
gold='../data/english/dev/wsj_dev.conll06'
train_file='../tmp/wsj_train.fold.cx'
test_file='../tmp/wsj_dev.cx'

sent_parser='../tmp/sent.fold.parser'
IOB_sent_parser='../tmp/IOB_test.fold.parser'

baseline_output='../tmp/wsj_dev.fold.baseline.conll06'



echo run_dev_fold.sh

# # baseline
# python unit_parser_main.py -baseline -train $train_file $sent_parser
# python unit_parser_main.py -baseline -test $test_file $sent_parser $baseline_output

# baseline + IOB feature
for i in 1 2 3 4 5 6 7 8
do
    IOB_output=../tmp/wsj_dev.fac.$i.conll06
    python unit_parser_main.py -IOB -train $train_file $IOB_sent_parser
    python unit_parser_main.py -IOB -test $test_file $IOB_sent_parser $IOB_output
done


# # results
echo baseline
perl eval07.pl -q -p -g $gold -s $baseline_output

for i in 1 2 3 4 5 6 7 8
do
    echo $i
    IOB_output=../tmp/wsj_dev.fac.$i.conll06
    perl eval07.pl -q -p -g $gold -s $IOB_output
done




