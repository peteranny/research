import sys,os
_, model_filename = sys.argv
from lib import progress

fin_filename = model_filename
progress("reading %s..."%fin_filename)
import numpy
U,I = dict(),dict()
with open(model_filename) as fin:
    line = fin.readline()
    nUsers,K = map(int,line.split())
    progress("%d users, K=%d"%(nUsers,K),br=True)
    for j in range(nUsers):
        line = fin.readline()
        u,vec = line.split(':')
        u,vec = int(u), numpy.array(map(float,vec.split()))
        assert len(vec)==K
        U[u] = vec
    line = fin.readline()
    nItems,K_ = map(int,line.split())
    assert K_==K # dimension of U,I should be identical
    progress("%d items, K=%d"%(nItems,K),br=True)
    for j in range(nItems):
        line = fin.readline()
        i,vec = line.split(':')
        i,vec = int(i), numpy.array(map(float,vec.split()))
        assert len(vec)==K
        I[i] = vec

fout_filename = "%s.predict"%model_filename
progress("writing %s..."%fout_filename)
users,items = U.keys(),I.keys()
with open(fout_filename, "w") as fout:
    for u in users:
        for i in items:
            fout.write("%d\t%d\t%f\n"%(u,i,numpy.dot(U[u],I[i])))

progress("done",br=True)

