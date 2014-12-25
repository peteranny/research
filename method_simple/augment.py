from __future__ import division
import sys,numpy
sys.path.append("..")
_,candidate_filename,model_filename,exposure_filename,clicked_filename,predict_filename = sys.argv
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
    nUsers,K = map(int,line.split())
    progress("%d users, K=%d"%(nUsers,K), br=True)

    # U matrix
    for j in range(nUsers):
        line = fin.readline()
        u,vec = line.split(':')
        u,vec = int(u), numpy.array(map(float,vec.split()))
        assert len(vec)==K
        U[u] = vec

    # I nRows & nCols
    line = fin.readline()
    nItems,K_ = map(int,line.split())
    assert K_==K # dimension of U,I should be identical
    progress("%d items, K=%d"%(nItems,K), br=True)

    # I matrix
    for j in range(nItems):
        line = fin.readline()
        i,vec = line.split(':')
        i,vec = int(i), numpy.array(map(float,vec.split()))
        assert len(vec)==K
        I[i] = vec

# output
fout_filename = "%s.predict"%model_filename
users,items = U.keys(),I.keys()
with open(fout_filename, "w") as fout:
    progress("writing %s..."%fout_filename)
    for u in users:
        for i in items:
            r_ = numpy.dot(U[u],I[i])
            fout.write("%d\t%d\t%f\n"%(u,i,r_))

progress("done",br=True)

