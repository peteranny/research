### mk_analysis_rmse

from __future__ import division
import sys
_,data_dirpath,nDiv,method_name = sys.argv
nDiv = int(nDiv)
from lib import progress, gen_path, gen_data_filename, gen_mk_out_filename

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

### rmse for each time division
rmse_at = {}
for d in range(1, nDiv): # 1, 2, ..., nDiv-1
    ### read predicted ratings
    fin_filename = gen_path(method_name, gen_data_filename(d, nDiv, "train.model.predict"))
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

    rmse_at[d] = rmse

fout_filename = gen_path(method_name, gen_mk_out_filename())
with open(fout_filename, "w") as fout:
    progress("writing %s..."%fout_filename)
    for d in range(1, nDiv):
        fout.write("%f\n"%rmse_at[d])

### plot
progress("plotting...")
import matplotlib.pyplot as plt
X = range(1,nDiv)
Y = [rmse_at[x] for x in X]
plt.plot(X, Y, 'o-')
plt.xlabel("Time")
plt.ylabel("RMSE")
plt.show()

progress("done", br=True)

