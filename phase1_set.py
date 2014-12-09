import sys,os
_, data_dirpath, data_end_d, train_end_at_d = sys.argv
data_end_d = int(data_end_d)
train_end_at_d = int(train_end_at_d)
from lib import progress,gen_data_filename,gen_path

# set training data
ratings_train = []
if train_end_at_d == 1:
    # initial training data
    fin_filename = gen_path(data_dirpath, gen_data_filename(1,data_end_d))
    progress("raading %s..."%fin_filename)
    with open(fin_filename) as fin:
        for line in fin:
            u,i,r,t = map(int,line.split())
            ratings_train.append((u,i,r,t))
else:
    # training extended from the previous training data
    fin_filename = gen_data_filename(train_end_at_d-1, data_end_d, "train")
    progress("reading %s..."%fin_filename)
    with open(fin_filename) as fin:
        for line in fin:
            u,i,r,t = map(int,line.split())
            ratings_train.append((u,i,r,t))
    fin_filename = gen_data_filename(train_end_at_d-1, data_end_d, "train.model.predict.recommend.examine")
    progress("reading %s..."%fin_filename)
    with open(fin_filename) as fin:
        for line in fin:
            u,i,r,t = map(int,line.split())
            if (u,i,r,t) not in ratings_train:
                ratings_train.append((u,i,r,t))
progress("%d training ratings"%len(ratings_train), br=True)

fout_filename = gen_data_filename(train_end_at_d,data_end_d,"train")
progress("writing %s..."%fout_filename)
with open(fout_filename, "w") as fout:
    for u,i,r,t in ratings_train:
        fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))

# set testing data
ratings_test = []
for d in range(train_end_at_d+1, data_end_d+1):
    fin_filename = gen_path(data_dirpath, gen_data_filename(d,data_end_d))
    progress("raading %s..."%fin_filename)
    with open(fin_filename) as fin:
        for line in fin:
            u,i,r,t = map(int,line.split())
            if (u,i,r,t) not in ratings_train:
                ratings_test.append((u,i,r,t))
progress("%d testing ratings"%len(ratings_test), br=True)

fout_filename = gen_data_filename(train_end_at_d,data_end_d,"test")
progress("writing %s..."%fout_filename)
with open(fout_filename, "w") as fout:
    for u,i,r,t in ratings_test:
        fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))

progress("done", br=True)

