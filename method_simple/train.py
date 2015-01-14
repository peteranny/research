from __future__ import division
import sys,os,numpy,copy
sys.path.append("..")
from collections import defaultdict
_,train_filename,users_filename,items_filename,candidates_filename,model_filename,predict_filename = sys.argv
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

# initialize
u_ratings,i_ratings = defaultdict(list),defaultdict(list)
rated = defaultdict(bool)
for x in ratings:
    u,i,r,t = x
    u_ratings[u].append(x)
    i_ratings[i].append(x)
    rated[u,i] = True
mu = numpy.mean([r for u,i,r,t in ratings])
bu = {u: numpy.mean([r - numpy.mean([s for v,j,s,tt in i_ratings[i]]) for u,i,r,t in u_ratings[u]]) \
        if len(u_ratings[u])>0 else 0 for u in users}
bi = {i: numpy.mean([r - numpy.mean([s for v,j,s,tt in u_ratings[u]]) for u,i,r,t in i_ratings[i]]) \
        if len(i_ratings[i])>0 else 0 for i in items}

# train
progress("training...")
D = 5
steps = 10
eta = 1e-2
lmd = 0.02
wm = 0.005
U,I = dict(),dict()
for u in users:
    U[u] = numpy.random.rand(D)
for i in items:
    I[i] = numpy.random.rand(D)
E = float('inf')
for step in xrange(steps):
    while True:
        newU,newI = copy.deepcopy(U),copy.deepcopy(I)
        for u in users:
            for d in range(D):
                dE = 0
                for u,i,r,t in u_ratings[u]:
                    r_ = mu + bu[u] + bi[i] + numpy.dot(U[u],I[i])
                    dE += ( 2*(r - r_)*(-I[i][d]) + lmd*2*U[u][d] )
                newU[u][d] = U[u][d] - eta*dE
        for i in items:
            for d in range(D):
                dE = 0
                for u,i,r,t in i_ratings[i]:
                    r_ = mu + bu[u] + bi[i] + numpy.dot(U[u],I[i])
                    dE += ( 2*(r - r_)*(-U[u][d]) + lmd*2*I[i][d] )
                newI[i][d] = I[i][d] - eta*dE
        newE = 0
        for u,i,r,t in ratings:
            r_ = mu + bu[u] + bi[i] + numpy.dot(newU[u],newI[i])
            newE += (r - r_)**2 + lmd*sum([newU[u][d]**2 + newI[i][d]**2 for d in range(D)])
        progress("step %d... eta=%.2e, E=%.2f"%(step,eta,newE))
        if newE>E:
            eta /= 2
            continue
        else:
            eta *= 1.05
            break
    U,I = newU,newI
    E = newE

# output model
fout_filename = model_filename
with open(model_filename, "w") as fout:
    progress("writing %s..."%fout_filename)
    fout.write("%d %d\n"%(len(U),D))
    for u in sorted(U):
        fout.write("%d:%s\n"%(u," ".join(map(str,U[u]))))
    fout.write("%d %d\n"%(len(I),D))
    for i in sorted(I):
        fout.write("%d:%s\n"%(i," ".join(map(str,I[i]))))

# output predict
fin_filename = candidates_filename
candidates = []
with open(fin_filename) as fin:
    progress("reading %s..."%fin_filename)
    for line in fin:
        u,i = line.split()
        u,i = int(u),int(i)
        candidates.append((u,i))

fout_filename = predict_filename
with open(fout_filename, "w") as fout:
    progress("writing %s..."%fout_filename)
    for u,i in candidates:
        try:
            r_ = mu + bu[u] + bi[i] + numpy.dot(U[u],I[i])
        except:
            r_ = mu + bu[u] + bi[i]
        fout.write("%d\t%d\t%f\n"%(u,i,r_))

progress("done",br=True)

