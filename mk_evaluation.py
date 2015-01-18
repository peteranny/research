### mk_analysis.py

from __future__ import division
from lib import *
import matplotlib.pyplot as plt
import sys
_,method_dirpath,nDiv = sys.argv
nDiv = int(nDiv)

### rmse for each time division
rmse_at = {}
for d in range(0, nDiv): # 1, 2, ..., nDiv-1
    ### read test ratings
    fin_filename = gen_path(method_dirpath, \
            gen_data_filename(d,nDiv,"test"))
    ratings = []
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r,t = line.split()
            u,i,r,t = int(u),int(i),int(r),int(t)
            ratings.append((u,i,r,t))

    ### read augmented ratings
    fin_filename = gen_path(method_dirpath, \
            gen_data_filename(d,nDiv,"train.candidates.predict.augment"))
    RIs = []
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r_ = line.split()
            u,i,r_ = int(u),int(i),float(r_)
            RIs.append((u,i,r_))

    ### format
    ui_ratings,ui_RIs = {},{}
    for u,i,r,t in ratings:
        ui_ratings[u,i] = r
    for u,i,r_ in RIs:
        ui_RIs[u,i] = r_

    ### RMSE
    rmse = 0
    N = 0
    for u,i in ui_ratings:
        r = ui_ratings[u,i]
        r_ = ui_RIs[u,i]
        rmse += (r - r_)**2
        N += 1
    rmse /= N
    rmse **= 1/2

    rmse_at[d] = rmse

### plot
progress("plotting RMSE...")
X = range(0,nDiv)
Y = [rmse_at[x] for x in X]
plt.subplot(2,1,1)
plt.plot(X, Y, 'o-')
plt.xlabel("Time")
plt.ylabel("RMSE")
plt.title("RMSE")

### exposure-stratified recall
recall_at = {}
for d in range(0, nDiv):
    ### read item exposure
    fin_filename = gen_path(method_dirpath, gen_data_filename(d,nDiv,"train.exposure"))
    exposure = {}
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            i,e = line.split(':')
            i,e = int(i),int(e)
            exposure[i] = e

    ### read passed ratings
    fin_filename = gen_path(method_dirpath, gen_data_filename(d, nDiv, "train.candidates.predict.augment.recommend.passed"))
    passed_ratings = []
    with open(fin_filename) as fin:
        for line in fin:
            u,i,r,t = line.split()
            u,i,r,t = int(u),int(i),int(r),int(t)
            passed_ratings.append((u,i,r,t))

    ### read test ratings
    fin_filename = gen_path(method_dirpath, gen_data_filename(d, nDiv, "test"))
    test_ratings = []
    with open(fin_filename) as fin:
        for line in fin:
            u,i,r,t = line.split()
            u,i,r,t = int(u),int(i),int(r),int(t)
            test_ratings.append((u,i,r,t))

    ### item recall weights
    beta = 1/3
    w_i = {}
    for i in exposure:
        w_i[i] = 1/exposure[i]**beta

    ### recall
    recall = sum([w_i[i] for u,i,r,t in passed_ratings]) \
            / sum([w_i[i] for u,i,r,t in test_ratings])
    
    recall_at[d] = recall

### plot
progress("plotting recall...")
X = range(0, nDiv)
Y = [recall_at[x] for x in X]
plt.subplot(2,1,2)
plt.plot(X, Y, "o-")
plt.xlabel("Time")
plt.ylabel("Recall")
plt.title("recall")

progress("showing figure...")
plt.show()

progress("done", br=True)

