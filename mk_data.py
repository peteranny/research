import sys
assert len(sys.argv)==3
nDiv = int(sys.argv[2])
dirname = sys.argv[1]

def __pg(msg, br=False):
    import sys
    sys.stdout.write("\r%s\033[K%s"%(msg, "\n" if br else ""))
    sys.stdout.flush()

__pg("reading data...")
fin_name = "../data/movieLen/ml-100k/u.data"
ratings = []
with open(fin_name, "r") as fin:
    for line in fin:
        u,i,r,t = map(int, line.split())
        ratings.append((u,i,r,t))

__pg("processing data...")
from collections import defaultdict
t_ratings = defaultdict(dict)
for u,i,r,t in ratings:
    t_ratings[t][(u,i)] = r

def gen_path(dirname, filename):
    import os
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return "%s/%s"%(dirname, filename)

fout_name = gen_path(dirname, "data.dat")
import math
timeline = sorted(t_ratings.keys())
timeIndex_chunkSize = int(math.ceil(len(timeline)/nDiv))
for j in range(nDiv):
    __pg("part %d..."%(j+1))
    with open("%s_%din%d%s"%(fout_name[:fout_name.index('.')],j+1,nDiv,fout_name[fout_name.index('.'):]), "w") as fout:
        for t in range(timeline[j*timeIndex_chunkSize], timeline[(j+1)*timeIndex_chunkSize] if j<nDiv-1 else timeline[-1]+1):
            for (u,i),r in t_ratings[t].iteritems():
                fout.write("%d\t%d\t%d\n"%(u,i,r))

__pg("users...")
with open(gen_path(dirname, "users.dat"), "w") as fout:
    users = set([u for u,i,r,t in ratings])
    for u in sorted(users):
        fout.write("%d\n"%u)

__pg("items...")
with open(gen_path(dirname, "items.dat"), "w") as fout:
    items = set([i for u,i,r,t in ratings])
    for i in sorted(items):
        fout.write("%d\n"%i)

__pg("done", br=True)

