import sys
_, data_dirpath, nDiv = sys.argv
nDiv = int(nDiv)
from lib import progress,gen_data_filename,gen_path

fin_filename = "../data/movieLen/ml-100k/u.data"
progress("reading %s..."%fin_filename)
ratings = []
with open(fin_filename, "r") as fin:
    for line in fin:
        u,i,r,t = map(int, line.split())
        ratings.append((u,i,r,t))
progress("%d ratings"%len(ratings),br=True)

progress("filtering...")
from collections import Counter
exposure = Counter([i for u,i,r,t in ratings])
nRatings_per_d = 10
ratings = list(filter(lambda (u,i,r,t):exposure[i]>nDiv*nRatings_per_d, ratings))

progress("processing data...")
from collections import defaultdict
t_ratings = defaultdict(dict)
for u,i,r,t in ratings:
    t_ratings[t][(u,i)] = r

import math
timeline = sorted(t_ratings.keys())
timeIndex_chunkSize = int(math.ceil(len(timeline)/nDiv))
for d in range(nDiv):
    fout_filename = gen_path(data_dirpath, gen_data_filename(d+1,nDiv), create=True)
    progress("writing %s..."%fout_filename)
    with open(fout_filename, "w") as fout:
        t_start = timeline[d*timeIndex_chunkSize]
        t_end = timeline[(d+1)*timeIndex_chunkSize] if d<nDiv-1 else timeline[-1]+1
        for t in range(t_start,t_end):
            for (u,i),r in t_ratings[t].iteritems():
                fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))

fout_filename = gen_path(data_dirpath, "users.dat", create=True)
progress("writing%s..."%fout_filename)
with open(fout_filename, "w") as fout:
    users = set([u for u,i,r,t in ratings])
    for u in sorted(users):
        fout.write("%d\n"%u)

fout_filename = gen_path(data_dirpath, "items.dat", create=True)
progress("writing %s..."%fout_filename)
with open(fout_filename, "w") as fout:
    items = set([i for u,i,r,t in ratings])
    for i in sorted(items):
        fout.write("%d\n"%i)

fout_filename = gen_path(data_dirpath, "data.analysis", create=True)
progress("writing %s..."%fout_filename)
with open(fout_filename, "w") as fout:
    exposure = {}
    for d in range(nDiv):
        exposure[d] = defaultdict(int)
        with open(gen_path(data_dirpath, gen_data_filename(d+1,nDiv))) as fin:
            for line in fin:
                u,i,r,t = map(int, line.split())
                exposure[d][i] += 1
    fout.write("item\t%s\n"%("\t".join(["div_%d"%(d+1) for d in range(nDiv)])))
    for i in sorted(items):
        fout.write("%d:\t"%i)
        for d in range(nDiv):
            fout.write("%d\t"%exposure[d][i])
        fout.write("\n")

progress("done", br=True)

