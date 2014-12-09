import sys
_, recommend_filename, test_filename = sys.argv
from lib import progress

fin_filename = test_filename
progress("reading %s..."%fin_filename)
ratings = []
with open(fin_filename) as fin:
    for line in fin:
        u,i,r,t = map(int,line.split())
        ratings.append((u,i,r,t))
progress("%d testing ratings"%len(ratings), br=True)

fin_filename = recommend_filename
progress("reading %s..."%fin_filename)
recomm = {}
with open(fin_filename) as fin:
    for line in fin:
        u,iis = line.split(':')
        u = int(u)
        iis = map(int,iis.split())
        recomm[u] = iis

progress("processing...")
from collections import defaultdict
u_ratings = defaultdict(list)
for u,i,r,t in ratings:
    u_ratings[u].append((u,i,r,t))

fout_filename = "%s.examine"%recommend_filename
progress("writing %s..."%fout_filename)
with open(fout_filename, "w") as fout:
    for u in u_ratings:
        for u,i,r,t in u_ratings[u]:
            if i in recomm[u]:
                fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))

progress("done", br=True)

