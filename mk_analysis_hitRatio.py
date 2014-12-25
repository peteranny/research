### mk_analysis_hitRatio

from __future__ import division
import sys
_,data_dirpath,nDiv,method_name,nMonitor = sys.argv
nDiv,nMonitor = int(nDiv),int(nMonitor)
from lib import progress, gen_path, gen_data_filename, gen_mk_out_filename

### read ratings
fin_filename = gen_path(data_dirpath, "ratings.dat")
progress("reading %s..."%fin_filename)
ratings = []
with open(fin_filename) as fin:
    for line in fin:
        u,i,r,t = line.split()
        u,i,r,t = int(u),int(i),int(r),int(t)
        ratings.append((u,i,r,t))

### make item quality
from collections import defaultdict
i_ratings = defaultdict(list)
for u,i,r,t in ratings:
    i_ratings[i].append(r)
import numpy
quality_of = {}
for i,rs in i_ratings.iteritems():
    m = numpy.mean(rs)
    v = numpy.std(rs)
    n = len(rs)
    quality_of[i] = (m,v,n)

### read item initial exposure
fin_filename = gen_path(data_dirpath, "data.analysis")
progress("reading %s..."%fin_filename)
init_exposure = {}
with open(fin_filename) as fin:
    for i,line in enumerate(fin):
        if i==0: continue ### header
        i,xs = line.split(':')
        i,xs = int(i),map(int,xs.split())
        init_exposure[i] = xs[0]

### choose monitored items (those with least exposure)
monitor_items = sorted(init_exposure, key=init_exposure.get)
monitor_items = monitor_items[0:nMonitor] #TODO

### see its recommendation over all divisions
import numpy
info_of = {}
for j,m_i in enumerate(monitor_items): ### for each monitored items
    progress("writing %d-th item..."%j)
    info_at = {}
    for d in range(1, nDiv): ### 1, 2, ..., nDiv-1
        fin_filename = gen_path(method_name, gen_data_filename(d, nDiv, "train.model.predict.recommend"))
        recomm_num = 0
        with open(fin_filename) as fin:
            for line in fin:
                u,iis = line.split(':')
                u,iis = int(u),list(map(int,iis.split()))
                if m_i in iis:
                    recomm_num += 1 ### item has been recommended

        fin_filename = gen_path(method_name, gen_data_filename(d, nDiv, "train.model.predict.recommend.passed"))
        hit_num = 0
        hit_time = []
        with open(fin_filename) as fin:
            for line in fin:
                u,i,r,t = line.split()
                u,i,r,t = int(u),int(i),int(r),int(t)
                if i==m_i:
                    hit_num += 1 ### item has been successfully recommended
                    hit_time.append(t) ### the time item should be rated originally
        info_at[d] = (recomm_num, hit_num, hit_time)

    info_of[m_i] = info_at

### output result
fout_filename = gen_path(method_name, gen_mk_out_filename())
with open(fout_filename, "w") as fout:
    progress("writing %s..."%fout_filename)
    fout.write("i/#/%%/T\t%s\n"%"\t".join(["div_%d"%d for d in range(1,nDiv)]))
    for m_i in monitor_items:
        m,v,n = quality_of[m_i]
        fout.write("%d:exp=%d,quality=%.1f,std=%.2f,n=%d\n"%(m_i, init_exposure[m_i], m, v, n))
        fout.write("\t%s\n"%("\t".join(["%d"%hit_num for d,(recomm_num,hit_num,hit_time) in info_of[m_i].items()])))
        fout.write("\t%s\n"%("\t".join(["%.1f%%"%(hit_num/recomm_num*100) if recomm_num>0 else "--" for d,(recomm_num,hit_num,hit_time) in info_of[m_i].items()])))
        fout.write("\t%s\n"%("\t".join(["%d"%int(numpy.median(hit_time)) if hit_num>0 else "--" for d,(recomm_num,hit_num,hit_time) in info_of[m_i].items()])))

### plot
progress("plotting...")
import matplotlib.pyplot as plt
plt.subplot(3, 1, 1)
plt.xlabel("Time")
plt.ylabel("#Hits")
for m_i in monitor_items:
    m,v,n = quality_of[m_i]
    info_at = info_of[m_i]
    X = range(1, nDiv)
    Y = [{d:hit_num for d,(recomm_num,hit_num,hit_time) in info_at.items()}[x] for x in X]
    plt.plot(X, Y, 'o-')
plt.legend([m_i for m_i in monitor_items])
plt.subplot(3, 1, 2)
plt.xlabel("Time")
plt.ylabel("Hit%")
for m_i in monitor_items:
    m,v,n = quality_of[m_i]
    info_at = info_of[m_i]
    X = range(1, nDiv)
    Y = [{d:hit_num/recomm_num if recomm_num>0 else 0 for d,(recomm_num,hit_num,hit_time) in info_at.items()}[x] for x in X]
    plt.plot(X, Y, 'o-')
plt.legend([m_i for m_i in monitor_items])
plt.subplot(3, 1, 3)
plt.xlabel("Time")
plt.ylabel("Midium hit time")
for m_i in monitor_items:
    m,v,n = quality_of[m_i]
    info_at = info_of[m_i]
    X = [d for d,hit_num in {d:hit_num for d,(recomm_num,hit_num,hit_time) in info_at.items()}.items() if hit_num>0]
    Y = [{d:int(numpy.median(hit_time)) if hit_num>0 else 0 for d,(recomm_num,hit_num,hit_time) in info_at.items()}[x] for x in X]
    plt.plot(X, Y, 'o-')
plt.legend([m_i for m_i in monitor_items])
plt.show()

progress("done", br=True)

