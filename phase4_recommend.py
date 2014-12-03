import sys,os
assert len(sys.argv)==5
_,predict_filename,users_filename,items_filename,k = sys.argv
recommend_filename = "%s.recommend"%os.path.basename(predict_filename)
k = int(k)
import pg

pg.write("reading %s..."%predict_filename)
ratings = []
with open(predict_filename) as fin:
    for line in fin:
        u,i,r_ = line.split()
        u = int(u)
        i = int(i)
        r_ = float(r_)
        ratings.append((u,i,r_))

pg.write("reading %s..."%users_filename)
users = []
with open(users_filename) as fin:
    for line in fin:
        u = int(line)
        users.append(u)
pg.write("%d users"%len(users),br=True)

pg.write("reading %s..."%items_filename)
items = []
with open(items_filename) as fin:
    for line in fin:
        u = int(line)
        items.append(u)
pg.write("%d items"%len(items),br=True)

pg.write("recommending and writing %s..."%recommend_filename)
from collections import defaultdict
u_ratings = defaultdict(list)
for u,i,r_ in ratings:
    u_ratings[u].append((r_,i))
with open(recommend_filename, "w") as fout:
    for u,xs in u_ratings.iteritems():
        fout.write("%d:%s\n"%(u," ".join(map(lambda (r_,i):str(i),sorted(xs, reverse=True)[:k]))))

pg.write("done", br=True)

