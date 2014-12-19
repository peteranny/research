from __future__ import division
import sys,os,numpy,copy
sys.path.append("..")
from collections import defaultdict
_,train_filename,users_filename,items_filename,model_filename = sys.argv
import lib
def progress(msg, br=False):
    lib.progress("[TRAIN] %s"%msg,br)

# read ratings
fin_filename = train_filename
ratings = []
with open(fin_filename) as fin:
    progress("train:reading %s..."%fin_filename)
    for line in fin:
        u,i,r,t = map(int, line.split())
        ratings.append((u,i,r,t))
progress("%d ratings"%len(ratings),br=True)

# read users
fin_filename = users_filename
users = []
with open(fin_filename) as fin:
    progress("reading %s..."%fin_filename)
    for line in fin:
        u = int(line)
        users.append(u)
progress("%d users"%len(users),br=True)

# read items
fin_filename = items_filename
items = []
with open(fin_filename) as fin:
    progress("reading %s..."%fin_filename)
    for line in fin:
        u = int(line)
        items.append(u)
progress("%d items"%len(items),br=True)

# interpolate
progress("progressing data...")
rm = 2
ui_ratings = {}
for u in users:
    for i in items:
        ui_ratings[u,i] = rm
for u,i,r,t in ratings:
    ui_ratings[u,i] = r
users_of = {i:[] for i in items}
items_of = {u:[] for u in users}
for u,i,r,t in ratings:
    users_of[i].append((u,r))
    items_of[u].append((i,r))

# train
progress("training...")
K = 5
steps = 10
eta = 0.01
lmd = 0.02
U,I = dict(),dict()
for u in users:
    U[u] = numpy.random.rand(K)
for i in items:
    I[i] = numpy.random.rand(K)
E = float('inf')
for step in xrange(steps):
    oldU,oldI = copy.deepcopy(U),copy.deepcopy(I)
    oldE = E
    while True:
        progress("step %d... eta=%.2e, E=%.2f"%(step,eta,E))
        for u in users:
            for k in range(K):
                dE = 0
                for i,r in items_of[u]:
                    dE += 2*(r - numpy.dot(oldU[u],oldI[i]))*(-oldI[i][k])
                dE += lmd*2*oldU[u][k]
                U[u][k] = oldU[u][k] - eta*dE
        for i in items:
            for k in range(K):
                dE = 0
                for u,r in users_of[i]:
                    dE += 2*(r - numpy.dot(oldU[u],oldI[i]))*(-oldU[u][k])
                dE += lmd*2*oldI[i][k]
                I[i][k] = oldI[i][k] - eta*dE
        E = 0
        for u in users:
            for k in range(K):
                E += U[u][k]**2
        for i in items:
            for k in range(K):
                E += I[i][k]**2
        E *= lmd
        for u,i,r,t in ratings:
            r_ = numpy.dot(U[u],I[i])
            E += (r - r_)**2
        if E>oldE:
            eta /= 2
            continue
        else:
            eta *= 1.05
            break

# output
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

