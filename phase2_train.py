import sys,os
assert len(sys.argv)==4
_,train_filename,users_filename,items_filename = sys.argv
model_filename = "%s.model"%os.path.basename(train_filename)
import pg

pg.write("reading %s..."%train_filename)
ratings = []
with open(train_filename) as fin:
    for line in fin:
        u,i,r = map(int, line.split())
        ratings.append((u,i,r))
pg.write("%d ratings"%len(ratings),br=True)

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

pg.write("interpolating...")
from collections import defaultdict
R = dict()
for u,i,r in ratings:
    R[u,i] = r
for u in users:
    for i in items:
        if (u,i) not in R:
            R[u,i] = 1e-5
ratings = [(u,i,r) for (u,i),r in R.iteritems()]
pg.write("matrix size=%d"%len(ratings),br=True)

pg.write("training...")
K = 2
steps = 10
alpha = 0.02
beta = 0.02
import numpy
users = [u for u,i,r in ratings]
items = [i for u,i,r in ratings]
U,I = dict(),dict()
for u in users:
    U[u] = numpy.random.rand(K)
for i in items:
    I[i] = numpy.random.rand(K)
for step in xrange(steps):
    pg.write("%d..."%step)
    for u,i,r in ratings:
        e = r - numpy.dot(U[u],I[i])
        for k in xrange(K):
            U[u][k] += alpha * (2 * e * I[i][k] - beta * U[u][k])
            I[i][k] += alpha * (2 * e * U[u][k] - beta * I[i][k])

pg.write("writing %s..."%model_filename,br=True)
with open(model_filename, "w") as fout:
    fout.write("%d %d\n"%(len(U),K))
    for u in sorted(U):
        fout.write("%d:%s\n"%( u," ".join(map(str,U[u])) ))
    fout.write("%d %d\n"%(len(I),K))
    for i in sorted(I):
        fout.write("%d:%s\n"%( i," ".join(map(str,I[i])) ))

pg.write("done",br=True)

