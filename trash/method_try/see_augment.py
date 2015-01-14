def msg(msg,br=False):
    import sys
    sys.stderr.write("\r%s%s"%(msg,"\n" if br else ""))
#alphas = [0.1*x for x in range(1,11)]
#alphas = [x for x in range(11)]
#alphas = [10*x for x in range(1,11)]
#alphas = [0.01*x for x in range(1,11)]
#alphas = [0.001*x for x in range(1,11)]

ratings = {}
fin_filename = "data_1_in_10.dat.train.model.predict"
with open(fin_filename) as fin:
    for line in fin:
        u,i,r = line.split()
        u,i,r = int(u),int(i),float(r)
        ratings[u,i] = r

ratings_ = {}
fin_filename = "data_1_in_10.dat.train.model.predict.augment"
with open(fin_filename) as fin:
    for line in fin:
        u,i,r_ = line.split()
        u,i,r_ = int(u),int(i),float(r_)
        ratings_[u,i] = r_

exposure = {}
fin_filename = "data_1_in_10.dat.train.exposure"
with open(fin_filename) as fin:
    for line in fin:
        i,e = line.split(':')
        i,e = int(i),int(e)
        exposure[i] = e

data = []
for u,i in ratings:
    data.append((u,i,ratings[u,i],ratings_[u,i],exposure[i]))
import random
#data = random.sample(data, 100)
data = filter(lambda (u,i,x,y,e):i==269 or i==1, data)

msg("plotting...")
import matplotlib.pyplot as plt
X = map(lambda (u,i,x,y,e):x, data)
Y = map(lambda (u,i,x,y,e):y, data)
S = map(lambda (u,i,x,y,e):e, data)
plt.scatter(X,Y,c='b',s=S)
plt.plot([-1,100],[-1,100])
plt.xlabel("ratings")
plt.ylabel("ratings_")
plt.axis([0,max(X),0,max(Y)])
plt.show()

msg("done",br=True)

