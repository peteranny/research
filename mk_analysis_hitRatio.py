### mk_analysis_hitRatio

from __future__ import division
import sys
_,data_dirpath,nDiv,nMonitor = sys.argv
nDiv,nMonitor = int(nDiv),int(nMonitor)
from lib import progress, gen_path, gen_data_filename, gen_mk_out_filename

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
fout_filename = gen_mk_out_filename()
progress("write %s..."%fout_filename)
with open(fout_filename, "w") as fout:
    fout.write("i\t%s\n"%"\t".join(["div_%d"%d for d in range(1,nDiv)]))
    ### for each monitored items
    for m_i in monitor_items:
        d_info = []
        for d in range(1, nDiv): ### for each prediction file
            fin_filename = gen_data_filename(d, nDiv, "train.model.predict.recommend")
            recomm_num = 0
            with open(fin_filename) as fin:
                for line in fin:
                    u,iis = line.split(':')
                    u,iis = int(u),list(map(int,iis.split()))
                    if m_i in iis:
                        recomm_num += 1 ### item has been recommended

            fin_filename = gen_data_filename(d, nDiv, "train.model.predict.recommend.examine")
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
        fout.write("%d:\t%d\n"%(m_i, init_exposure[m_i]))
        fout.write("num\t%s\n"%("\t".join(["%d"%hit_num for recomm_num,hit_num,hit_midtime in d_info])))
        fout.write("ratio\t%s\n"%("\t".join(["%.2f"%(hit_num/recomm_num) for recomm_num,hit_num,hit_midtime in d_info])))
        fout.write("midtime\t%s\n"%("\t".join(["%d"%int(hit_midtime) if hit_num>0 else "--" for recomm_num,hit_num,hit_midtime in d_info])))

progress("done", br=True)

