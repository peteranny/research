phase_path=../
data_path=../data10/
topK=20
dd=1 2 3 4 5 6 7 8 9
data_end_d=10
all:
	for d in $(dd); \
	do \
	echo "=== $${d} out of $(data_end_d) ==="; \
	python $(phase_path)phase1_set.py $(data_path) $(data_end_d) $${d} ;\
	python train.py data_$${d}_in_$(data_end_d).dat.train $(data_path)users.dat $(data_path)items.dat data_$${d}_in_$(data_end_d).dat.train.model ;\
	python $(phase_path)phase3_predict.py data_$${d}_in_$(data_end_d).dat.train.model ;\
	python $(phase_path)phase4_recommend.py data_$${d}_in_$(data_end_d).dat.train.model.predict $(topK) ;\
	python $(phase_path)phase5_examine.py data_$${d}_in_$(data_end_d).dat.train.model.predict.recommend data_$${d}_in_$(data_end_d).dat.test ;\
	done
ls:
	ls -l
clean:
	rm -rf .* *~

