#!/bin/bash
run_path=../
data_path=../dataMini-cut/
train_lang=python
train_prog=train.py
augment_lang=python
augment_prog=no-augment.py
topK=1
delta=5

### start ###
data_end_d=$((`head -n 1 $data_path/data.analysis | awk '{print NF}'` - 1))
for d in `seq 0 $(($data_end_d-1))`;
do
    data_filename=data_${d}_in_${data_end_d}.dat
    progress=$d/$(($data_end_d-1))
	echo "===== $progress ====="
	python ${run_path}run.py \
        $data_path \
        $d \
        $train_lang \
        $train_prog \
        $augment_lang \
        $augment_prog \
        $topK \
        $delta \
        11111
    if [ $? -ne 0 ]; then
        exit 1
    fi
done
exit 0

