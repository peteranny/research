### phase4_recommend

import sys,os
_,predict_filename,train_filename,k = sys.argv
k = int(k)
from lib import progress

### read predict file
fin_filename = predict_filename
progress("reading %s..."%fin_filename)
ratings_ = []
with open(fin_filename) as fin:
    for line in fin:
        u,i,r_ = line.split()
        u,i,r_ = int(u),int(i),float(r_)
        ratings_.append((u,i,r_))
progress("%d predicted ratings"%len(ratings_),br=True)

### users and items
users = list(set([u for u,i,r_ in ratings_]))
items = list(set([i for u,i,r_ in ratings_]))

### read training ratings
fin_filename = train_filename
progress("reading %s..."%fin_filename)
ratings = []
with open(fin_filename) as fin:
    for line in fin:
        u,i,r,t = map(int, line.split())
        ratings.append((u,i,r,t))
progress("%d training ratings"%len(ratings),br=True)

### convert training rating format (in u,i)
ui_ratings = {}
for u,i,r,t in ratings:
    ui_ratings[u,i] = r

### candidate items (predicted ratings) for each user
progress("filtering past (u,i) pairs...")
from collections import defaultdict
u_ratings = defaultdict(list)
for u,i,r_ in ratings_:
    if (u,i) in ratings: continue ### skip (u,i) already in training data
    u_ratings[u].append((i,r_))

### write recommendation
fout_filename = "%s.recommend"%predict_filename
progress("writing %s..."%fout_filename)
with open(fout_filename, "w") as fout:
    for u,xs in u_ratings.iteritems():
        recom_items = sorted(xs, key=lambda (i,r_):r_, reverse=True) ### sort by predicted ratings
        recom_items = recom_items[:k] ### pick top-K
        recom_items = map(lambda (i,_r):i, recom_items)
        fout.write("%d:%s\n"%(u," ".join(map(str, recom_items))))

progress("done", br=True)

