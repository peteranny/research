class Rating:
	_u_n_digits = 0
	_i_n_digits = 0
	_r_n_digits = 0
	def __init__(self, user, item, rate):
		self.user = user
		self.item = item
		self.rate = rate
	def __str__(self):
		return ("Rating(u=%-"+str(self._u_n_digits)+"d;i=%-"+str(self._i_n_digits)+"d;r=%-"+str(self._r_n_digits)+"d)")%(self.user, self.item, self.rate)
	def __repr__(self):
		return self.__str__()


fname = "../data/ml-100k/u.data"
fin = open(fname, "r")
ratings = []
for line in fin:
	prt = map(int, line.split())
	user = prt[0]
	item = prt[1]
	rate = prt[2]
	time = prt[3]
	ratings.append(Rating(user, item, rate))
import math
Rating._u_n_digits = math.ceil(math.log10(max([r.user for r in ratings])))
Rating._i_n_digits = math.ceil(math.log10(max([r.item for r in ratings])))
Rating._r_n_digits = math.ceil(math.log10(max([r.rate for r in ratings])))

'''
for u in list(set([r.user for r in ratings])):
	ratings_u = list(map(lambda x:x.rate,filter(lambda x:x.user==u, ratings)))
	print u,
	for k in [5,4,3,2,1]:
		print ratings_u.count(k),
	print ""
'''


def GD(ratings, K, lmd, eta, dlt, num_iter):
	import numpy
	# initialize
	U = dict()
	I = dict()
	for u in set(map(lambda x:x.user, ratings)):
		U[u] = numpy.random.rand(K)
	for i in set(map(lambda x:x.item, ratings)):
		I[i] = numpy.random.rand(K)
	# gradient descent
	import sys
	def __pg(msg, linebreak=False):
		sys.stdout.write("\r"+msg+"".join([" " for n in xrange(__pg.msglen-len(msg))])+("\n" if linebreak else ""))
		__pg.msglen = len(msg)
	__pg.msglen = 0
	for t in xrange(1,num_iter+1):
		_U = U.copy()
		_I = I.copy()
		# improve U
		for u in U:
			for k in xrange(K):
				__pg("\rtraining... t=%d u=%d k=%d"%(t,u,k))
				dE = []
				for r in filter(lambda x:x.user == u, ratings):
					i = r.item
					r = r.rate
					_r = numpy.dot(_U[u], _I[i])
					dE.append(2*(r - _r)*(-_I[i][k]))
				dE = numpy.mean(dE)
				#dE += 2*lmd*_U[u][k]
				U[u][k] -= eta*dE
		# improve I
		for i in I:
			for k in xrange(K):
				__pg("\rtraining... t=%d i=%d k=%d"%(t,i,k))
				dE = []
				for r in filter(lambda x:x.item == i, ratings):
					u = r.user
					r = r.rate
					_r = numpy.dot(_U[u], _I[i])
					dE.append(2*(r - _r)*(-_U[u][k]))
				dE = numpy.mean(dE)
				#dE += 2*lmd*_I[i][k]
				I[i][k] -= eta*dE
		'''
		err = 0
		for r in ratings:
			u = r.user
			i = r.item
			r = r.rate
			_r = numpy.dot(U[u], I[i])
			err += (r - _r)**2
		#for u in U:
		#	err += lmd*numpy.dot(U[u], U[u])
		#for i in I:
		#	err += lmd*numpy.dot(I[i], I[i])
		err /= len(ratings)
		if err < dlt:
			break
		'''
	__pg("\rtraining done",linebreak=True)
	return U, I

fout_name = "test.out"
ratings = ratings[:] #TODO
K = 5
lmd = 0.01
eta = 0.1
dlt = 0.01
num_iter = 10
num_sample_u = 10

import numpy
'''
U,I = GD(ratings, K, lmd, eta, dlt, num_iter)
for junk,r in filter(lambda x:x[0]<10, enumerate(ratings)):
	u = r.user
	i = r.item
	print r, numpy.dot(U[u], I[i])
'''

## for a given u draw corresponding f-s figure
fout = open(fout_name, "w")
import random
u_sample = random.sample(set(map(lambda x:x.user, ratings)), num_sample_u)
items = list(map(lambda x:x.item, ratings))
fout.write("user\titem\tpredicted_rating\trating\n")
U_all,I_all = GD(ratings, K, lmd, eta, dlt, num_iter)
for u in u_sample:
	rated_items = dict([(r.item, r) for r in filter(lambda x:x.user == u, ratings)])
	for i in rated_items:
		_r = numpy.dot(U_all[u], I_all[i])
		r = rated_items[i].rate
		print "user=%d item=%d predicted_rating=%.1f"%(u,i,_r) + (" rating=%d"%r if r != -1 else "")
		fout.write("%d\t%d\t%.1f\t%d\n"%(u,i,_r,r))
fout.close()

