import numpy

R = [[1,2,3],[4,5,6],[7,8,9]]
K = 5
lmd = 0.01
eta = 0.0002
dlt = 0.01
num_iter = 1000

H = len(R)
W = len(R[0])
R = numpy.matrix(R)
P = numpy.random.rand(H,K)
Q = numpy.random.rand(K,W)
for t in xrange(num_iter):
	_P = P.copy()
	_Q = Q.copy()
	for i in xrange(H):
		for k in xrange(K):
			dE = 0
			for j in xrange(W):
				dE += -2*(R[i,j] - numpy.dot(_P[i,:],_Q[:,j]))*_Q[k,j]
			dE += 2*lmd*_P[i,k]
			P[i,k] -= eta*dE
	for k in xrange(K):
		for j in xrange(W):
			dE = 0
			for i in xrange(H):
				dE += -2*(R[i,j] - numpy.dot(_P[i,:],_Q[:,j]))*_P[i,k]
			dE += 2*lmd*_Q[k,j]
			Q[k,j] -= eta*dE
	err = 0
	for i in xrange(H):
		for j in xrange(W):
			err += (R[i,j] - numpy.dot(P[i,:],Q[:,j]))**2
			for k in xrange(K):
				err += lmd*(P[i,k]**2 + Q[k,j]**2)
	if err < dlt:
		break

print R
print numpy.dot(P,Q)
