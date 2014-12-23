### mk_analysis_expStratifiedRecall

from __future__ import division
import sys
_,data_dirpath,nDiv,method_name = sys.argv
nDiv = int(nDiv)
from lib import progress, gen_path, gen_data_filename, gen_mk_out_filename

### items 
fin_filename = gen_path(data_dirpath, "items.dat")
items = []
with open(fin_filename) as fin:
    progress("reading %s..."%fin_filename)
    for line in fin:
        i = int(line)
        items.append(i)

recall_at = {}
for d in range(1, nDiv):
    ### read train data
    fin_filename = gen_path(method_name, gen_data_filename(d, nDiv, "train"))
    train_ratings = []
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r,t = line.split()
            u,i,r,t = int(u),int(i),float(r),int(t)
            train_ratings.append((u,i,r,t))

    ### read test data
    fin_filename = gen_path(method_name, gen_data_filename(d, nDiv, "test"))
    test_ratings = []
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r,t = line.split()
            u,i,r,t = int(u),int(i),float(r),int(t)
            test_ratings.append((u,i,r,t))

    ### read passed ratings
    fin_filename = gen_path(method_name, gen_data_filename(d, nDiv, "train.model.predict.recommend.passed"))
    passed_ratings = []
    with open(fin_filename) as fin:
        for line in fin:
            u,i,r,t = line.split()
            u,i,r,t = int(u),int(i),int(r),int(t)
            passed_ratings.append((u,i,r,t))

    ### item exposure
    i_exposure = {i:0 for i in items}
    for u,i,r,t in train_ratings:
        i_exposure[i] += 1

    ### item recall weights
    beta = 1/3
    i_weight = {}
    for i,n in i_exposure.iteritems():
        i_weight[i] = 1/n**beta

    ### recall nominator
    recall = 0
    for u,i,r,t in passed_ratings:
        recall += i_weight[i]

    ### recall dominator
    recall_sum = 0
    for u,i,r,t in test_ratings:
        recall_sum += i_weight[i]

    recall /= recall_sum
    recall_at[d] = recall

### output result
fout_filename = gen_path(method_name, gen_mk_out_filename())
with open(fout_filename, "w") as fout:
    for d in range(1, nDiv):
        fout.write("%f\n"%recall_at[d])

progress("done", br=True)

