from __future__ import division
import sys
_,data_dirpath,nDiv,rm = sys.argv
nDiv,rm = int(nDiv),float(rm)
from lib import progress, gen_path, gen_data_filename

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

fin_filename = gen_path(data_dirpath, "users.dat")
progress("reading %s..."%fin_filename)
users = []
with open(fin_filename) as fin:
    for line in fin:
        u = int(line)
        users.append(u)
progress("%d users"%len(users),br=True)

fin_filename = gen_path(data_dirpath, "items.dat")
progress("reading %s..."%fin_filename)
items = []
with open(fin_filename) as fin:
    for line in fin:
        u = int(line)
        items.append(u)
progress("%d items"%len(items),br=True)

progress("processing ui_ratings...")
for u in users:
    for i in items:
        if (u,i) not in ui_ratings:
            ui_ratings[u,i] = rm

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

from collections import defaultdict
start_d_items = defaultdict(list)
for i,d in start_d.items():
    start_d_items[d].append(i)

fout_filename = "plot_1.out"
with open(fout_filename, "w") as fout:
    for sd in range(1):
        d_rmse = []
        for d in range(sd, nDiv-1): # for each predict file
            fin_filename = gen_data_filename(d+1, nDiv, "train.model.predict")
            progress("reading %s..."%fin_filename)
            pratings = []
            with open(fin_filename) as fin:
                for line in fin:
                    u,i,r = line.split()
                    u,i,r = int(u),int(i),float(r)
                    pratings.append((u,i,r))
            ui_pratings = {}
            for u,i,r in pratings:
                ui_pratings[u,i] = r
        
            rmse = 0
            for i in start_d_items[sd]:
                for u in users:
                    r = ui_ratings[u,i]
                    r_ = ui_pratings[u,i]
                    rmse += (r - r_)**2
            rmse /= len(start_d_items[sd])*len(users)
            rmse **= 1/2
            d_rmse.append(rmse)
        fout.write("%s\n"%("\t".join(["%.3f"%rmse for rmse in d_rmse])))

progress("done", br=True)

