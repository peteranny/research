### mk_analysis_rmse

from __future__ import division
import sys
_,data_dirpath,nDiv = sys.argv
nDiv = int(nDiv)
from lib import progress, gen_path, gen_data_filename

### read ratings
fin_filename = gen_path(data_dirpath, "ratings.dat")
progress("reading %s..."%fin_filename)
ratings = []
with open(fin_filename) as fin:
    for line in fin:
        u,i,r,t = line.split()
        u,i,r,t = int(u),int(i),float(r),int(t)
        ratings.append((u,i,r,t))
ui_ratings = {}
for u,i,r,t in ratings:
    ui_ratings[u,i] = r
progress("%d ratings"%len(ratings), br=True)

### read users
fin_filename = gen_path(data_dirpath, "users.dat")
progress("reading %s..."%fin_filename)
users = []
with open(fin_filename) as fin:
    for line in fin:
        u = int(line)
        users.append(u)
progress("%d users"%len(users),br=True)

### read items
fin_filename = gen_path(data_dirpath, "items.dat")
progress("reading %s..."%fin_filename)
items = []
with open(fin_filename) as fin:
    for line in fin:
        u = int(line)
        items.append(u)
progress("%d items"%len(items),br=True)

'''
### add imputed ratings
progress("processing ui_ratings...")
for u in users:
    for i in items:
        if (u,i) not in ui_ratings:
            ui_ratings[u,i] = rm
'''

'''
### read data histogram (to figure out item's starting time)
fin_filename = gen_path(data_dirpath, "data.analysis")
progress("reading %s..."%fin_filename)
start_d = {}
with open(fin_filename) as fin:
    for i,line in enumerate(fin):
        if i==0: continue
        i,xs = line.split(':')
        i,xs = int(i),map(int,xs.split())
        d = 0
        for dd in range(0, nDiv):
            if xs[dd]>0: break
            d += 1
        assert d<=nDiv-1
        start_d[i] = d

### classify items by its starting time
from collections import defaultdict
start_d_items = defaultdict(list)
for i,d in start_d.items():
    start_d_items[d].append(i)
'''

### rmse for each time division
fout_filename = "%s.out"%sys.argv[0][sys.argv[0].index('_')+1:sys.argv[0].rindex('.')]
with open(fout_filename, "w") as fout:
    for d in range(nDiv-1): # no prediction result for the last time division
        ### read predicted ratings
        fin_filename = gen_data_filename(d+1, nDiv, "train.model.predict")
        progress("reading %s..."%fin_filename)
        ratings_ = []
        with open(fin_filename) as fin:
            for line in fin:
                u,i,r_ = line.split()
                u,i,r_ = int(u),int(i),float(r_)
                ratings_.append((u,i,r_))

        ### convert preditecd ratings format
        ui_ratings_ = {}
        for u,i,r_ in ratings_:
            ui_ratings_[u,i] = r_

        rmse = 0
        total_num = 0
        for u,i in ui_ratings:
            r = ui_ratings[u,i]
            r_ = ui_ratings_[u,i]
            rmse += (r - r_)**2
            total_num += 1
        rmse /= total_num
        rmse **= 1/2
        fout.write("%f\n"%rmse)

progress("done", br=True)

