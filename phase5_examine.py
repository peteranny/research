import sys
assert len(sys.argv)==3
_,test_filename,recommend_filename = sys.argv

ratings = list()
with open(test_filename) as fin:
    for line in fin:
        u,i,r,t = map(int,line.split())
        ratings.append((u,i,r,t))

recomm = dict()
with open(recommend_filename) as fin:
    for line in fin:
        u,iis = line.split(,':')
        u = int(u)
        iis = map(int,iis.split())
        recomm[u] = iis

from collections import defaultdict
u_ratings = defaultdict(list)
for u,i,r,t in ratings:
    u_ratings[u].append((u,i,r,t))

with open(examine_filename, "w") as fout:
    for u in u_ratings:
        for u,i,r,t in u_ratings[u]:
            if i in recomm[u]:
                fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))

