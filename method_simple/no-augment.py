from __future__ import division
from collections import defaultdict
import sys,numpy,math
sys.path.append("..")
_,predict_filename,model_filename,exposure_filename,clicked_filename,augment_filename = sys.argv
import lib
def progress(msg, br=False):
    lib.progress("[AUGMENT] %s"%msg,br)

# read ratings
fin_filename = predict_filename
ratings = []
with open(fin_filename) as fin:
    progress("reading %s..."%fin_filename)
    for line in fin:
        u,i,r = line.split()
        u,i,r = int(u),int(i),float(r)
        ratings.append((u,i,r))
ui_ratings = {(u,i):r for u,i,r in ratings}
users = sorted(list(set([u for u,i,r in ratings])))
items = sorted(list(set([i for u,i,r in ratings])))

'''
# P(u|i)=sum{P(u|d)*P(d|i)}
fin_filename = model_filename
U,I = dict(),dict()
with open(model_filename) as fin:
    progress("reading %s..."%fin_filename)

    # U nRows & nCols
    line = fin.readline()
    nUsers,D = map(int,line.split())
    progress("%d users, D=%d"%(nUsers,D), br=True)

    # U matrix
    for j in range(nUsers):
        line = fin.readline()
        u,vec = line.split(':')
        u,vec = int(u), numpy.array(map(float,vec.split()))
        assert len(vec)==D
        U[u] = vec

    # I nRows & nCols
    line = fin.readline()
    nItems,D_ = map(int,line.split())
    assert D_==D # dimension of U,I should be identical
    progress("%d items, D=%d"%(nItems,D), br=True)

    # I matrix
    for j in range(nItems):
        line = fin.readline()
        i,vec = line.split(':')
        i,vec = int(i), numpy.array(map(float,vec.split()))
        assert len(vec)==D
        I[i] = vec
clicked = defaultdict(bool)
with open(clicked_filename) as fin:
    progress("reading %s..."%fin_filename)
    for line in fin:
        u,i = line.split()
        u,i = int(u),int(i)
        clicked[u,i] = True
Pdi = {}
for n,i in enumerate(items):
    progress("%.1f%%... P(d|i)"%(n/len(items)*100))
    for d in range(D):
        Pdi[d,i] = abs(I[i][d])/sum(abs(I[i]))
Pud = {}
for n,u in enumerate(users):
    progress("%.1f%%... P(u|d)"%(n/len(users)*100))
    for d in range(D):
        Pud[u,d] = sum([Pdi[d,j] for j in items if clicked[u,j]])
        Pud[u,d] /= sum([Pdi[d,j] for j in items for v in users if clicked[v,j]])

# w_i
progress("w_i...")
exposure = {}
with open(exposure_filename) as fin:
    for line in fin:
        i,e = line.split(':')
        i,e = int(i),int(e)
        exposure[i] = e
beta = 1
#beta = 1/3
w_i = {i:1/exposure[i]**beta if exposure[i]>0 else 1 for i in items}
'''

# update RI
progress("updating RI...")
T = 0
K = 20
rM = 5
eta = 1e-2
alpha1 = 0
alpha2 = 0
E = float('inf')
delta = rM * K
ri = ui_ratings.copy()
for t in range(T):
    c_u = {u:sum([w_i[j]*ri[u,j] for j in items if (u,j) in ri]) - delta for u in users}
    while True:
        if eta<1e-20: break
        new_ri = ri.copy()
        for u,i in ri:
            Pui = sum([Pud[u,d]*Pdi[d,i] for d in range(D)])
            dE0 = (-2) * (ui_ratings[u,i] - ri[u,i])
            dE1 = (-2) * w_i[i] * Pui * (rM - ri[u,i])
            dE2 = math.exp(c_u[u]) * w_i[i]
            dE = dE0 + alpha1*dE1 + alpha2*dE2
            new_ri[u,i] = ri[u,i] - eta*dE

        c_u = {u:sum([w_i[j]*new_ri[u,j] for j in items if (u,j) in new_ri]) - delta for u in users}
        newE = 0
        for u,i in new_ri:
            Pui = sum([Pud[u,d]*Pdi[d,i] for d in range(D)])
            newE0 = (ui_ratings[u,i] - new_ri[u,i])**2
            newE1 = w_i[i] * Pui * (rM - new_ri[u,i])**2
            newE2 = math.exp(c_u[u])
            newE += newE0 + alpha1*newE1 + alpha2*newE2
        progress("t=%d, eta=%.2e... E = %.2e + %.2e * %.2e + %.2e * %.2e = %.2e" \
                %(t,eta,newE0,alpha1,newE1,alpha2,newE2,newE) )

        if newE > E:
            eta /= 2
            continue
        else:
            eta *= 1.05
            break
    ri = new_ri
    E = newE

# output
fout_filename = augment_filename
with open(fout_filename, "w") as fout:
    progress("writing %s..."%fout_filename)
    for u in users:
        for i in items:
            if (u,i) in ui_ratings:
                r_ = ri[u,i]
                fout.write("%d\t%d\t%f\n"%(u,i,r_))

progress("done",br=True)

