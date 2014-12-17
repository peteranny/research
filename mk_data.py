### mk_data

import sys
_,data_dirpath,nDiv,min_nRatings = sys.argv
nDiv,min_nRatings = int(nDiv),int(min_nRatings)
from lib import progress,gen_data_filename,gen_path

### read raw data
fin_filename = "../data/movieLen/ml-100k/u.data"
progress("reading %s..."%fin_filename)
ratings = []
with open(fin_filename, "r") as fin:
    for line in fin:
        u,i,r,t = map(int, line.split())
        ratings.append((u,i,r,t))
progress("%d ratings (raw data)"%len(ratings),br=True)

### filter items whose exposure not sufficient enough
progress("filtering...")
from collections import Counter
exposure = Counter([i for u,i,r,t in ratings])
ratings = list(filter(lambda (u,i,r,t):exposure[i]>min_nRatings, ratings))

### convert rating format (in time)
progress("processing data...")
from collections import defaultdict
t_ratings = defaultdict(dict)
for u,i,r,t in ratings:
    t_ratings[t][(u,i)] = r

### time division size
import math
timeline = sorted(t_ratings.keys())
timeIndex_chunkSize = int(math.ceil(len(timeline)/nDiv))

### filter items that does not appear in the first division
progress("filtering...")
d = 1
t_start = timeline[(d-1)*timeIndex_chunkSize]
t_end = timeline[d*timeIndex_chunkSize] if d!=nDiv else timeline[-1]+1
items = set()
for t in range(t_start,t_end):
    for (u,i),r in t_ratings[t].iteritems():
        items.add(i) ### use only items that appear at first
ratings = [(u,i,r,t) for u,i,r,t in ratings if i in items] ### ramake ratings
t_ratings = defaultdict(dict)
for u,i,r,t in ratings:
    t_ratings[t][(u,i)] = r ### remake t_ratings

### create ratings
fout_filename = gen_path(data_dirpath, "ratings.dat", create=True)
progress("writing %s..."%fout_filename)
with open(fout_filename, "w") as fout:
    for u,i,r,t in ratings:
        fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))
progress("%d ratings"%len(ratings),br=True)

### create data divisions
for d in range(1,nDiv+1):
    fout_filename = gen_path(data_dirpath, gen_data_filename(d,nDiv), create=True)
    progress("writing %s..."%fout_filename)
    with open(fout_filename, "w") as fout:
        t_start = timeline[(d-1)*timeIndex_chunkSize]
        t_end = timeline[d*timeIndex_chunkSize] if d!=nDiv else timeline[-1]+1
        for t in range(t_start,t_end):
            for (u,i),r in t_ratings[t].iteritems():
                fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))

### create users
fout_filename = gen_path(data_dirpath, "users.dat", create=True)
progress("writing%s..."%fout_filename)
with open(fout_filename, "w") as fout:
    users = set([u for u,i,r,t in ratings])
    for u in sorted(users):
        fout.write("%d\n"%u)
progress("%d users"%len(users),br=True)

### create items
fout_filename = gen_path(data_dirpath, "items.dat", create=True)
progress("writing %s..."%fout_filename)
with open(fout_filename, "w") as fout:
    items = set([i for u,i,r,t in ratings])
    for i in sorted(items):
        fout.write("%d\n"%i)
progress("%d items"%len(items),br=True)

### create analysis (item rating frequency)
fout_filename = gen_path(data_dirpath, "data.analysis", create=True)
progress("writing %s..."%fout_filename)
with open(fout_filename, "w") as fout:
    ### item exposure (item rating frequency) at division d
    exposure = {}
    for d in range(1,nDiv+1):
        exposure[d] = defaultdict(int)
        with open(gen_path(data_dirpath, gen_data_filename(d,nDiv))) as fin:
            for line in fin:
                u,i,r,t = map(int, line.split())
                exposure[d][i] += 1
    ### write item exposure over divisions
    fout.write("item\\t<\t%s\n"%("\t".join(["%d"%timeline[d*timeIndex_chunkSize] for d in range(1,nDiv+1)])))
    for i in sorted(items):
        fout.write("%d:\t"%i)
        for d in range(1,nDiv+1):
            fout.write("%d\t"%exposure[d][i])
        fout.write("\n")

progress("done", br=True)

