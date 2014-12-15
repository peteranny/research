### phase5_examine

import sys
_, recommend_filename, test_filename = sys.argv
from lib import progress

### read recommendation
fin_filename = recommend_filename
progress("reading %s..."%fin_filename)
recomm = {}
with open(fin_filename) as fin:
    for line in fin:
        u,iis = line.split(':')
        u,iis = int(u), map(int,iis.split())
        recomm[u] = iis

### read testing data (future)
fin_filename = test_filename
progress("reading %s..."%fin_filename)
ratings = []
with open(fin_filename) as fin:
    for line in fin:
        u,i,r,t = map(int,line.split())
        ratings.append((u,i,r,t))
progress("%d testing ratings"%len(ratings), br=True)

### convert test ratings (in u,i)
progress("processing...")
from collections import defaultdict
ui_ratings = {}
for u,i,r,t in ratings:
    ui_ratings[u,i] = (u,i,r,t)

### write recommendation that hits
fout_filename = "%s.examine"%recommend_filename
progress("writing %s..."%fout_filename)
with open(fout_filename, "w") as fout:
    for u in recomm:
        ### check if the recommendation hits
        for i in recomm[u]:
            if (u,i) in ui_ratings:
                u,i,r,t = ui_ratings[u,i]
                fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))

progress("done", br=True)

