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
i_quality = {}
for i,rs in i_ratings.iteritems():
    m = numpy.mean(rs)
    v = numpy.std(rs)
    n = len(rs)
    i_quality[i] = (m,v,n)

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
fout_filename = gen_path(method_name, gen_mk_out_filename())
with open(fout_filename, "w") as fout:
    fout.write("i/#/%%/T\t%s\n"%"\t".join(["div_%d"%d for d in range(1,nDiv)]))
    ### for each monitored items
    for j,m_i in enumerate(monitor_items):
        progress("writing %d-th item..."%j)
        d_info = []
        for d in range(1, nDiv): ### for each prediction file
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
            import numpy
            if hit_num > 0:
                hit_midtime = numpy.median(hit_time)

            d_info.append((recomm_num, hit_num, hit_midtime))
        m,v,n = i_quality[m_i]
        fout.write("%d:exp=%d,quality=%.1f,std=%.2f,n=%d\n"%(m_i, init_exposure[m_i], m, v, n))
        fout.write("\t%s\n"%("\t".join(["%d"%hit_num for recomm_num,hit_num,hit_midtime in d_info])))
        fout.write("\t%s\n"%("\t".join(["%.1f%%"%(hit_num/recomm_num*100) if recomm_num>0 else "--" for recomm_num,hit_num,hit_midtime in d_info])))
        fout.write("\t%s\n"%("\t".join(["%d"%int(hit_midtime) if hit_num>0 else "--" for recomm_num,hit_num,hit_midtime in d_info])))

progress("done", br=True)

