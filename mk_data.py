### mk_data

import sys,math,pprint
from collections import Counter,defaultdict
from lib import progress,gen_data_filename,gen_path
_,src_name = sys.argv

### read raw data
ratings = []
if src_name=="ml-100k":
    fin_filename = "../data/movieLen/ml-100k/u.data"
    with open(fin_filename, "r") as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r,t = map(int, line.split())
            ratings.append((u,i,r,t))
elif src_name=="ml-1m":
    fin_filename = "../data/movieLen/ml-1m/ratings.dat"
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r,t = line.split('::')
            u,i,r,t = int(u),int(i),int(r),int(t)
            ratings.append((u,i,r,t))
else:
    raise Exception("src_name : ml-100k / ml-1m")
progress("%d ratings (raw data)"%len(ratings),br=True)

### ask for min_nRatings
exposure = Counter([i for u,i,r,t in ratings])
while True:
    bin_size = int(raw_input("Enter the bin size (0 to end): "))
    if bin_size==0: break
    bins = defaultdict(int)
    for i,e in exposure.items():
        bins[e//bin_size*bin_size] += 1
    progress("exposure>: #items",br=True)
    progress(pprint.pformat(dict(bins), width=1), br=True)
min_nRatings = int(raw_input("Enter min number of ratings per item : "))

### ask for nDiv
nDiv = int(raw_input("Enter nDiv : "))

### ask for data_dirpath
data_dirpath = raw_input("Enter the data name : ")

### filter items whose exposure not sufficient enough
progress("filtering...")
ratings = list(filter(lambda (u,i,r,t):exposure[i]>=min_nRatings, ratings))

### convert rating format (in time)
progress("processing data...")
t_ratings = defaultdict(dict)
for u,i,r,t in ratings:
    t_ratings[t][(u,i)] = r

### time division size
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

