#!/usr/bin/python
#
# Created by Albert Au Yeung (2010)
#
# An implementation of matrix factorization
#
try:
    import numpy
except:
    print "This implementation requires the numpy module."
    exit(0)

###############################################################################

"""
@INPUT:
    R     : a matrix to be factorized, dimension N x M
    P     : an initial matrix of dimension N x K
    Q     : an initial matrix of dimension M x K
    K     : the number of latent features
    steps : the maximum number of steps to perform the optimisation
    alpha : the learning rate
    beta  : the regularization parameter
@OUTPUT:
    the final matrices P and Q
"""
def __pg(msg, br=False):
    import sys
    sys.stderr.write("\r%s\033[K"%(msg) + ("\n" if br else ""))
    sys.stderr.flush()

def matrix_factorization(ratings, K=1, steps=50, alpha=0.02, beta=0.02):
    nUsers = len([u for u,i,r in ratings])
    nItems = len([i for u,i,r in ratings])
    U,I = dict(),dict()
    for u in xrange(nUsers):
        U[u] = numpy.random.rand(K)
    for i in xrange(nItems):
        I[i] = numpy.random.rand(K)

    for step in xrange(steps):
        __pg("%d..."%step)
        for u,i,r in ratings:
            e = r - numpy.dot(U[u],I[i])
            for k in xrange(K):
                U[u][k] += alpha * (2 * e * I[i][k] - beta * U[u][k])
                I[i][k] += alpha * (2 * e * U[u][k] - beta * I[i][k])
    return U,I

###############################################################################

import sys
assert len(sys.argv)==3
train_filename = sys.argv[1]
model_filename = sys.argv[2]

ratings = []
with open(train_filename) as fin:
    for line in fin:
        u,i,r = map(int, line.split())
        ratings.append((u,i,r))
'''
R = [
     [5,3,0,1],
     [4,0,0,1],
     [1,1,0,5],
     [1,0,0,4],
     [0,1,5,4],
    ]
ratings = [
        (0,0,5), (0,1,3), (0,3,1),
        (1,0,4), (1,3,1),
        (2,0,1), (2,1,1), (2,3,5),
        (3,0,1), (3,3,4),
        (4,1,1), (4,2,5), (4,3,4)
        ]
'''

U,I = matrix_factorization(ratings, K=2)
for u,i,r in ratings:
    print "%d\t%d\t%d\t%.1f"%(u,i,r,numpy.dot(U[u],I[i]))
__pg("done",br=True)

