#!/bin/bash
run_path=../
data_path=../dataMini/
data_end_d=10
train_lang=python
train_prog=train.py
adjust_lang=python
adjust_prog=adjust.py
topK=5

for d in `seq 1 $(($data_end_d-1))`;
do
    data_filename=data_${d}_in_${data_end_d}.dat
    progress=$d/$(($data_end_d-1))
	echo "===== $progress ====="
	python ${run_path}run.py \
        $data_path \
        $d \
        $data_end_d \
        $train_lang \
        $train_prog \
        $adjust_lang \
        $adjust_prog \
        $topK \
        11111
done

exit 0

