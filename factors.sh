
gold='../data/english/dev/wsj_dev.conll06'
train_file='../tmp/wsj_train.fold.cx'
test_file='../tmp/wsj_dev.cx'
i=$1

echo run_dev_fold.sh

IOB_output=../tmp/wsj_dev.fac.$i.conll06
IOB_sent_parser=../tmp/fac.$i.parser

python unit_parser_main.py -fa$i -train $train_file $IOB_sent_parser
python unit_parser_main.py -fa$i -test $test_file $IOB_sent_parser $IOB_output

perl eval07.pl -q -p -g $gold -s $IOB_output





