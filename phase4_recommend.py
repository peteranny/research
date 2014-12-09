import sys,os
_, predict_filename, k = sys.argv
k = int(k)
from lib import progress

fin_filename = predict_filename
progress("reading %s..."%fin_filename)
ratings = []
with open(fin_filename) as fin:
    for line in fin:
        u,i,r_ = line.split()
        u = int(u)
        i = int(i)
        r_ = float(r_)
        ratings.append((u,i,r_))
progress("%d ratings"%len(ratings),br=True)

users = list(set([u for u,i,r_ in ratings]))
items = list(set([i for u,i,r_ in ratings]))

fout_filename = "%s.recommend"%predict_filename
progress("writing %s..."%fout_filename)
from collections import defaultdict
u_ratings = defaultdict(list)
for u,i,r_ in ratings:
    u_ratings[u].append((r_,i))
with open(fout_filename, "w") as fout:
    for u,xs in u_ratings.iteritems():
        fout.write("%d:%s\n"%(u," ".join(map(lambda (r_,i):str(i),sorted(xs, reverse=True)[:k]))))

progress("done", br=True)

