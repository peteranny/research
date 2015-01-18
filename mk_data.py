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

### ask for cut
timeline = sorted(set([t for u,i,r,t in ratings]))
nDiv = 2
timeIndex_chunkSize = int(math.ceil(len(timeline)/nDiv))
d_cut = 1
t_cut = timeline[d_cut*timeIndex_chunkSize if d_cut<=nDiv-1 else float('inf')]
progress("t_cut = %d"%(t_cut),br=True)

### filter items that does not appear at first
progress("filtering...")
items = set([i for u,i,r,t in ratings if t<t_cut]) # leave only items that appear before cut
ratings = filter(lambda (u,i,r,t):i in items, ratings)
progress("%d ratings and %d items before cut"%(len(ratings),len(items)),br=True)

### ask for min_nRatings
exposure = Counter([i for u,i,r,t in ratings])
while True:
    progress("Enter exposure bin size (0 to end) : ")
    bin_size = int(raw_input())
    if bin_size==0: break
    bins = defaultdict(int)
    for i,e in exposure.items():
        bins[e//bin_size*bin_size] += 1
    progress("exposure>: #items",br=True)
    progress(pprint.pformat(dict(bins), width=1), br=True)
progress("Enter min number of ratings per item : ")
min_nRatings = int(raw_input())

### filter items whose exposure not sufficient enough
progress("filtering...")
ratings = list(filter(lambda (u,i,r,t):exposure[i]>=min_nRatings, ratings))
progress("%d ratings of items with exposure >= %d"%(len(ratings),min_nRatings),br=True)

### split ratings before cut
progress("splitting ratings before t=%d..."%t_cut)
all_ratings = ratings
prior_ratings = filter(lambda (u,i,r,t):t<t_cut, ratings)
ratings = filter(lambda (u,i,r,t):t>=t_cut, ratings)
progress("%d prior ratings and %d ratings"%(len(prior_ratings),len(ratings)),br=True)

### ask for nDiv
progress("Enter nDiv: ")
nDiv = int(raw_input())

### ask for data_dirpath
data_dirpath = raw_input("Enter the data name (and start saving) : ")

### convert rating format (in time)
progress("processing data...")
t_ratings = defaultdict(list)
for data in ratings:
    u,i,r,t = data
    t_ratings[t].append(data)

### time division size
timeline = sorted(t_ratings.keys())
timeIndex_chunkSize = int(math.ceil(len(timeline)/nDiv))

### create ratings
fout_filename = gen_path(data_dirpath, "ratings.dat", create=True)
with open(fout_filename, "w") as fout:
    progress("writing %s..."%fout_filename)
    for u,i,r,t in all_ratings:
        fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))
progress("%d ratings"%len(all_ratings),br=True)

### create users
fout_filename = gen_path(data_dirpath, "users.dat", create=True)
users = set([u for u,i,r,t in all_ratings])
with open(fout_filename, "w") as fout:
    progress("writing %s..."%fout_filename)
    for u in sorted(users):
        fout.write("%d\n"%u)
progress("%d users"%len(users),br=True)

### create items
fout_filename = gen_path(data_dirpath, "items.dat", create=True)
items = set([i for u,i,r,t in all_ratings])
with open(fout_filename, "w") as fout:
    progress("writing %s..."%fout_filename)
    for i in sorted(items):
        fout.write("%d\n"%i)
progress("%d items"%len(items),br=True)

### create data divisions
for d in range(0,nDiv+1):
    fout_filename = gen_path(data_dirpath, gen_data_filename(d,nDiv), create=True)
    with open(fout_filename, "w") as fout:
        progress("writing %s..."%fout_filename)
        if d==0:
            for u,i,r,t in prior_ratings:
                fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))
        else:
            t_start = timeline[(d-1)*timeIndex_chunkSize]
            t_end = timeline[d*timeIndex_chunkSize] if d!=nDiv else timeline[-1]+1
            for t in range(t_start,t_end):
                for u,i,r,tt in t_ratings[t]:
                    fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))

### create analysis (item rating frequency)
fout_filename = gen_path(data_dirpath, "data.analysis", create=True)
with open(fout_filename, "w") as fout:
    progress("writing %s..."%fout_filename)
    exposure_at = {} ### item exposure (item rating frequency) at division d
    for d in range(0,nDiv+1):
        exposure_at[d] = defaultdict(int)
        fin_filename = gen_path(data_dirpath, gen_data_filename(d,nDiv))
        with open(fin_filename) as fin:
            progress("reading %s..."%fin_filename)
            for line in fin:
                u,i,r,t = map(int, line.split())
                exposure_at[d][i] += 1

    ### write item exposure over divisions
    fout.write("item\tt<%d\t%s\n"%(timeline[0], \
            "\t".join(["t>%d"%timeline[(d-1)*timeIndex_chunkSize] \
                        for d in range(1,nDiv+1)])))
    for i in sorted(items):
        fout.write("%d\t"%i)
        for d in range(0,nDiv+1):
            fout.write("%d\t"%exposure_at[d][i])
        fout.write("\n")

progress("done", br=True)

