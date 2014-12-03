import sys,os
assert len(sys.argv)==4
_,users_filename,items_filename,model_filename = sys.argv
predict_filename = "%s.predict"%os.path.basename(model_filename)
import pg

pg.write("reading %s..."%model_filename)
import numpy
U,I = dict(),dict()
with open(model_filename) as fin:
    line = fin.readline()
    nUsers,K = map(int,line.split())
    for j in range(nUsers):
        line = fin.readline()
        u,vec = line.split(':')
        u,vec = int(u), numpy.array(map(float,vec.split()))
        assert len(vec)==K
        U[u] = vec
    line = fin.readline()
    nItems,K = map(int,line.split())
    for j in range(nItems):
        line = fin.readline()
        i,vec = line.split(':')
        i,vec = int(i), numpy.array(map(float,vec.split()))
        assert len(vec)==K
        I[i] = vec

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

pg.write("predicting and writing %s..."%predict_filename)
with open(predict_filename, "w") as fout:
    for u in users:
        for i in items:
            fout.write("%d\t%d\t%f\n"%(u,i,numpy.dot(U[u],I[i])))

pg.write("done",br=True)

