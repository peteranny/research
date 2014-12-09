import sys,os
_, train_filename, users_filename, items_filename, model_filename = sys.argv
sys.path.append("..")
from lib import progress

fin_filename = train_filename
progress("reading %s..."%fin_filename)
ratings = []
with open(fin_filename) as fin:
    for line in fin:
        u,i,r,t = map(int, line.split())
        ratings.append((u,i,r,t))
progress("%d ratings"%len(ratings),br=True)

fin_filename = users_filename
progress("reading %s..."%fin_filename)
users = []
with open(fin_filename) as fin:
    for line in fin:
        u = int(line)
        users.append(u)
progress("%d users"%len(users),br=True)

fin_filename = items_filename
progress("reading %s..."%fin_filename)
items = []
with open(fin_filename) as fin:
    for line in fin:
        u = int(line)
        items.append(u)
progress("%d items"%len(items),br=True)

progress("interpolating...")
from collections import defaultdict
R = dict()
for u,i,r,t in ratings:
    R[u,i] = (r,t)
for u in users:
    for i in items:
        if (u,i) not in R:
            R[u,i] = (1e-5,-1) # impute rating, invalid time
ratings = [(u,i,r,t) for (u,i),(r,t) in R.iteritems()]
progress("matrix size=%d"%len(ratings),br=True)

progress("training...")
K = 2
steps = 10
alpha = 0.002
beta = 0.02
import numpy
users = [u for u,i,r,t in ratings]
items = [i for u,i,r,t in ratings]
U,I = dict(),dict()
for u in users:
    U[u] = numpy.random.rand(K)
for i in items:
    I[i] = numpy.random.rand(K)
#import warnings
#warnings.filterwarnings('error')
for step in xrange(steps):
    progress("step %d..."%step)
    for u,i,r,t in ratings:
        e = r - numpy.dot(U[u],I[i])
        for k in xrange(K):
            #try:
            U[u][k] += alpha * (2 * e * I[i][k] - beta * U[u][k])
            I[i][k] += alpha * (2 * e * U[u][k] - beta * I[i][k])
            #except:
            #    print e
            #    exit()

fout_filename = model_filename
progress("writing %s..."%fout_filename)
with open(model_filename, "w") as fout:
    fout.write("%d %d\n"%(len(U),K))
    for u in sorted(U):
        fout.write("%d:%s\n"%(u," ".join(map(str,U[u]))))
    fout.write("%d %d\n"%(len(I),K))
    for i in sorted(I):
        fout.write("%d:%s\n"%(i," ".join(map(str,I[i]))))

progress("done",br=True)

