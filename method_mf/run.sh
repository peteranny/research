#!/bin/bash
phase_path=../
data_path=../data20/
train_lang=python
train_prog=train.py
topK=20
data_end_d=20

for d in `seq 1 $(($data_end_d-1))`;
do
    data_filename=data_${d}_in_${data_end_d}.dat
    progress=$d/$(($data_end_d-1))
	echo "== $progress set =="
	python ${phase_path}phase1_set.py \
        $data_path \
        $data_end_d \
        $d
	echo "== $progress train =="
	python ${phase_path}phase2_train.py \
        ${data_filename}.train \
        ${data_path}users.dat \
        ${data_path}items.dat \
        $train_lang \
        $train_prog
	echo "== $d/$data_end_d predict =="
	python ${phase_path}phase3_predict.py \
        ${data_filename}.train.model
	echo "== $d/$data_end_d recommend =="
	python ${phase_path}phase4_recommend.py \
        ${data_filename}.train.model.predict \
        ${data_filename}.train \
        $topK
	echo "== $d/$data_end_d examine =="
	python ${phase_path}phase5_examine.py \
        ${data_filename}.train.model.predict.recommend \
        ${data_filename}.test
done

exit 0

