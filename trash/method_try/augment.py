from __future__ import division
from collections import defaultdict
import sys,numpy,math
sys.path.append("..")
_,predict_filename,model_filename,exposure_filename,clicked_filename,augment_filename = sys.argv
import lib
def progress(msg, br=False):
    lib.progress("[AUGMENT] %s"%msg,br)

# read model
fin_filename = model_filename
U,I = dict(),dict()
with open(model_filename) as fin:
    progress("reading %s..."%fin_filename)

    # U nRows & nCols
    line = fin.readline()
    nUsers,Z = map(int,line.split())
    progress("%d users, Z=%d"%(nUsers,Z), br=True)

    # U matrix
    for j in range(nUsers):
        line = fin.readline()
        u,vec = line.split(':')
        u,vec = int(u), numpy.array(map(float,vec.split()))
        assert len(vec)==Z
        U[u] = vec

    # I nRows & nCols
    line = fin.readline()
    nItems,Z_ = map(int,line.split())
    assert Z_==Z # dimension of U,I should be identical
    progress("%d items, Z=%d"%(nItems,Z), br=True)

    # I matrix
    for j in range(nItems):
        line = fin.readline()
        i,vec = line.split(':')
        i,vec = int(i), numpy.array(map(float,vec.split()))
        assert len(vec)==Z
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

# P(i|u)=sum{P(i|z)*P(z|u)} ... X
# P(u|i)=sum{P(u|z)*P(z|i)}
progress("P(u|i)...")
clicked = defaultdict(bool)
with open(clicked_filename) as fin:
    for line in fin:
        u,i = line.split()
        u,i = int(u),int(i)
        clicked[u,i] = True
items = sorted(I.keys())
Pzi = {}
for n,i in enumerate(items):
    progress("%.1f%%... P(z|i)"%(n/len(items)*100))
    for z in range(Z):
        Pzi[z,i] = abs(I[i][z])/sum(abs(I[i]))
users = sorted(U.keys())
Puz = {}
for n,u in enumerate(users):
    progress("%.1f%%... P(u|z)"%(n/len(users)*100))
    for z in range(Z):
        Puz[u,z] = sum([Pzi[z,j] for j in items if clicked[u,j]])
        Puz[u,z] /= sum([Pzi[z,j] for j in items for v in users if clicked[v,j]])

# w_i
progress("w_i...")
exposure = {}
with open(exposure_filename) as fin:
    for line in fin:
        i,e = line.split(':')
        i,e = int(i),int(e)
        exposure[i] = e
#beta = 1/3
beta = 1
w_i = {i:1/exposure[i]**beta if exposure[i]>0 else 1 for i in items}
#progress("w_i=%s"%str(w_i),br=True)

# update RI
progress("updating RI...")
def sigmoid(x):
    #progress("sigmoid(%f) = %f"%(x,1/(1+math.exp(-x))),br=True)
    return 1/(1 + math.exp(-x))
def d_sigmoid(x):
    return math.exp(-x) * sigmoid(x)**2
T = 100
topK = 1
rM = 5
eta = 1e-3
alpha1 = 1e+2
alpha2 = 1e+2
E = float('inf')
#delta_0 = {u:sum([w_i[j]*ui_ratings[u,j] for j in items if (u,j) in ui_ratings]) for u in users}
#delta = {u:topK * 5 * sum([w_i[j] for j in items if (u,j) in ui_ratings]) for u in users}
delta = rM * topK
ri = ui_ratings.copy()
for t in range(T):
    #progress("",br=True)
    #progress("t=%d"%t,br=True)
    #c_u = {u:delta_0[u] + delta[u] \
    #        - sum([w_i[j]*ri[u,j] for j in items if (u,j) in ri]) for u in users}
    c_u = {u:sum([w_i[j]*ri[u,j] for j in items if (u,j) in ri]) - delta for u in users}
    #progress("c_u=%s"%str(c_u),br=True)
    while True:
        if eta<1e-20: break
        new_ri = ri.copy()
        #progress("c_u=%s"%str(c_u),br=True)
        for u,i in ri:
            Pui = sum([Puz[u,z]*Pzi[z,i] for z in range(Z)])
            '''
            dE = (-2) * alpha * (ui_ratings[u,i] - ri[u,i]) \
                    + (1-alpha) * w_i[i] * Piu * \
                    ( d_sigmoid(c_u[u]) * w_i[i] * ri[u,i] - sigmoid(c_u[u]) )
            dE = (-2) * (ui_ratings[u,i] - ri[u,i]) \
                    + alpha * w_i[i] * Piu * \
                    ( d_sigmoid(c_u[u]) * w_i[i] * ri[u,i] - sigmoid(c_u[u]) )
            '''
            dE0 = (-2) * (ui_ratings[u,i] - ri[u,i])
            #dE2 = w_i[i] * Piu * (-1)
            #dE2 = w_i[i] * (-1)
            #dE2 = w_i[i] * \
            #        ( d_sigmoid(c_u[u]) * w_i[i] * ri[u,i] - sigmoid(c_u[u]) )
            dE1 = (-2) * w_i[i] * Pui * (rM - ri[u,i])
            dE2 = math.exp(c_u[u]) * w_i[i]
            dE = dE0 + alpha1*dE1 + alpha2*dE2
            new_ri[u,i] = ri[u,i] - eta*dE
            #if i==1 or i==269:
            #progress("u=%d, i=%d, eta * dE = %.2e * ( %.2e + %.2e * %.2e + %.2e * %.2e) = %.2e"%(u,i,eta,dE0,alpha1,dE1,dE),br=True)
            #progress("( dE1 = (-2) * %f * (%f - %f) = %f )"%(w_i[i],rM,ri[u,i],dE1),br=True)
            #    progress("( dE1 = (-2) * %.2e * %.2e * (%.2e - %.2e) = %.2e )"%(w_i[i],Pui,rM,ri[u,i],dE2),br=True)
            #progress("( dE2 = %f * (%f - %f) = %f )"%(w_i[i],d_sigmoid(c_u[u])*w_i[i]*ri[u,i],sigmoid(c_u[u]),dE2),br=True)
        #progress("new_ri=%s"%str(new_ri),br=True)

        c_u = {u:sum([w_i[j]*new_ri[u,j] for j in items if (u,j) in new_ri]) - delta for u in users}
        #progress("c_u=%s"%str(c_u),br=True)
        newE = 0
        for u,i in new_ri:
            Pui = sum([Puz[u,z]*Pzi[z,i] for z in range(Z)])
            '''
            newE += alpha * (ui_ratings[u,i] - new_ri[u,i])**2 \
                    + (1-alpha) * w_i[i] * sigmoid(c_u[u]) * Piu * (-new_ri[u,i])
            newE += (ui_ratings[u,i] - new_ri[u,i])**2 \
                    + alpha * w_i[i] * sigmoid(c_u[u]) * Piu * (-new_ri[u,i])
            '''
            newE0 = (ui_ratings[u,i] - new_ri[u,i])**2
            #newE2 = w_i[i] * Piu * (-new_ri[u,i])
            #newE2 = w_i[i] * (-new_ri[u,i])
            #newE2 = w_i[i] * (-new_ri[u,i]) * sigmoid(c_u[u])
            newE1 = w_i[i] * Pui * (rM - new_ri[u,i])**2
            newE2 = math.exp(c_u[u])
            newE += newE0 + alpha1*newE1 + alpha2*newE2
        #progress("eta=%.2e... E = %.2e + %f * %.2e = %.2e"%(eta,newE0,alpha1,newE1,newE), br=True)
        progress("t=%d, eta=%.2e... E = %.2e + %.2e * %.2e + %.2e * %.2e = %.2e" \
                %(t,eta,newE0,alpha1,newE1,alpha2,newE2,newE) )

        if newE > E:
            eta /= 2
            #progress("",br=True)
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
                Pui = Puz[u,z] * Pzi[z,i]
                fout.write("%d\t%d\t%f\t%.2e\n"%(u,i,r_,Pui))

progress("done",br=True)

