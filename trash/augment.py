from __future__ import division
from collections import defaultdict
import sys,numpy,math
sys.path.append("../")
import lib
_,predict_filename,model_filename,exposure_filename,clicked_filename,augment_filename,delta = sys.argv
delta = float(delta)

def progress(msg, br=False):
    lib.progress("[AUGMENT] %s"%msg,br)

# read model
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

# P(i|u)=sum{P(i|d)*P(d|u)} ... X
# P(u|i)=sum{P(u|d)*P(d|i)}
progress("P(u|i)...")
clicked = defaultdict(bool)
with open(clicked_filename) as fin:
    for line in fin:
        u,i = line.split()
        u,i = int(u),int(i)
        clicked[u,i] = True
items = sorted(I.keys())
Pdi = {}
for n,i in enumerate(items):
    progress("%.1f%%... P(d|i)"%(n/len(items)*100))
    Pdi_denominator = sum((abs(I[i])))
    for d in range(D):
        Pdi[d,i] = abs(I[i][d])/Pdi_denominator
users = sorted(U.keys())
Pud = {}
Pud_denominator = {}
for d in range(D):
    progress("%.1f%%... P(u|d)"%(n/len(users)*100))
    Pud_denominator[d] = sum([Pdi[d,j] for j in items for v in users if clicked[v,j]])
for n,u in enumerate(users):
    progress("%.1f%%... P(u|d)"%(n/len(users)*100))
    for d in range(D):
        Pud[u,d] = sum([Pdi[d,j] for j in items if clicked[u,j]])
        Pud[u,d] /= Pud_denominator[d]

# w_i
progress("w_i...")
exposure = {}
with open(exposure_filename) as fin:
    for line in fin:
        i,e = line.split(':')
        i,e = int(i),int(e)
        exposure[i] = e
beta = 1/3
#beta = 1
w_i = {i:1/exposure[i]**beta if exposure[i]>0 else 1 for i in items}
#progress("w_i=%s"%str(w_i),br=True)

# update RI
import warnings
warnings.filterwarnings('error')
def sigmoid(x):
    return 1/(1+math.exp(-x))
progress("updating RI...")
T = 5000
rM = 5
eta = 1e-3
alpha = 1e+2 * 1e+1 * 1e+1#1e+4
alpha_c = alpha# * sigmoid(sum(w_i.values()) - 1/4)# * 1e+1#1e+4 * numpy.linalg.norm(w_i.values(),5)
E = float('inf')
delta_c = delta
ri = ui_ratings.copy()
for t in range(T):
    alpha_c = alpha * sigmoid(sum(w_i.values()) - 1/3)# * 1e+1#1e+4 * numpy.linalg.norm(w_i.values(),5)
    #progress("",br=True)
    #progress("t=%d"%t,br=True)
    #c_u = {u:delta_0[u] + delta[u] \
    #        - sum([w_i[j]*ri[u,j] for j in items if (u,j) in ri]) for u in users}
    c_u = {u:sum([w_i[j]*ri[u,j] for j in items if (u,j) in ri]) - delta_c for u in users}
    #progress("c_u=%s"%str(c_u),br=True)
    while True:
        if eta<1e-100: break
        try:
            new_ri = ri.copy()
            #progress("c_u=%s"%str(c_u),br=True)
            for u,i in ri:
                Pui = sum([Pud[u,d]*Pdi[d,i] for d in range(D)])
                dE0 = (-2) * (ui_ratings[u,i] - ri[u,i])
                #dE1 = (-2) * (rM - ri[u,i])
                #dE1 = (-2) * Pui * (rM - ri[u,i])
                dE1 = (-2) * w_i[i] * Pui * (rM - ri[u,i])
                dEc = math.exp(c_u[u]) * w_i[i]
                dE = dE0 + alpha*dE1 + alpha_c*dEc
                new_ri[u,i] = ri[u,i] - eta*dE
                #if i==1 or i==269:
                #progress("u=%d, i=%d, eta * dE = %.2e * ( %.2e + %.2e * %.2e + %.2e * %.2e) = %.2e"%(u,i,eta,dE0,alpha1,dE1,dE),br=True)
                #progress("( dE1 = (-2) * %f * (%f - %f) = %f )"%(w_i[i],rM,ri[u,i],dE1),br=True)
                #    progress("( dE1 = (-2) * %.2e * %.2e * (%.2e - %.2e) = %.2e )"%(w_i[i],Pui,rM,ri[u,i],dE2),br=True)
                #progress("( dE2 = %f * (%f - %f) = %f )"%(w_i[i],d_sigmoid(c_u[u])*w_i[i]*ri[u,i],sigmoid(c_u[u]),dE2),br=True)
            #progress("new_ri=%s"%str(new_ri),br=True)
    
            c_u = {u:sum([w_i[j]*new_ri[u,j] for j in items if (u,j) in new_ri]) - delta_c for u in users}
            #progress("c_u=%s"%str(c_u),br=True)
            newE0,newE1,newEc = 0,0,0
            for u,i in new_ri:
                Pui = sum([Pud[u,d]*Pdi[d,i] for d in range(D)])
                newE0 += (ui_ratings[u,i] - new_ri[u,i])**2
                #newE1 += (rM - new_ri[u,i])**2
                #newE1 += Pui * (rM - new_ri[u,i])**2
                newE1 += w_i[i] * Pui * (rM - new_ri[u,i])**2
            for u in users:
                newEc += math.exp(c_u[u])
            newE = newE0 + alpha*newE1 + alpha_c*newEc
            #progress("eta=%.2e... E = %.2e + %f * %.2e = %.2e"%(eta,newE0,alpha1,newE1,newE), br=True)
            progress("t=%d, eta=%.2e... E = %.2e + %.2e * %.2e + %.2e * %.2e = %.2e" \
                    %(t,eta,newE0,alpha,newE1,alpha_c,newEc,newE) )
        except (OverflowError,Warning) as e:
            progress("t=%d, eta=%.2e... overflow"%(t,eta))
            ri,E,c_u = pre_ri,pre_E,pre_c
            eta /= 2
            continue

        if newE > E:
            eta /= 2
            #progress("",br=True)
            continue
        else:
            eta *= 1.05
            break
    pre_ri,pre_E,pre_c = ri,E,c_u
    ri,E = new_ri,newE

# output
fout_filename = augment_filename
with open(fout_filename, "w") as fout:
    progress("writing %s..."%fout_filename)
    for u in users:
        for i in items:
            if (u,i) in ui_ratings:
                r_ = ri[u,i]
                Pui = Pud[u,d] * Pdi[d,i]
                #fout.write("%d\t%d\t%f\t%.2e\n"%(u,i,r_,Pui))
                fout.write("%d\t%d\t%f\n"%(u,i,r_))

progress("done",br=True)

