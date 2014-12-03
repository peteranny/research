import sys,os
assert len(sys.argv)==4
_,data_dirpath,data_end_d,train_end_at_d = sys.argv
data_end_d = int(data_end_d)
train_end_at_d = int(train_end_at_d)
train_filename = "data_%din%d_train.dat"%(train_end_at_d,data_end_d)
test_filename = "data_%din%d_test.dat"%(train_end_at_d,data_end_d)
import pg

# set training data
ratings_train = []
if train_end_at_d == 1:
    # initial training data
    d = 1
    fin_filename = "%s/data_%din%d.dat"%(data_dirpath,d,data_end_d)
    pg.write("raading %s..."%fin_filename)
    with open(fin_filename) as fin:
        for line in fin:
            u,i,r,t = map(int,line.split())
            ratings_train.append((u,i,r,t))
else:
    # training extended from the previous training data
    fin_filename = "data_%din%d_train.dat"%(train_end_at_d-1,data_end_d)
    pg.write("reading %s..."%fin_filename)
    with open(fin_filename) as fin:
        for line in fin:
            u,i,r,t = map(int,line.split())
            ratings_train.append((u,i,r,t))
    fin_filename = "data_%din%d_train.dat.model.predict.recommend.examine"
    with open(fin_filename) as fin:
        for line in fin:
            u,i,r,t = map(int,line.split())
            if (u,i,r,t) not in ratings_train:
                ratings_train.append((u,i,r,t))

pg.write("writing %s..."%train_filename)
with open(train_filename, "w") as fout:
    for u,i,r in ratings_train:
        fout.write("%d\t%d\t%d\n"%(u,i,r))

# set testing data
ratings_test = []
for d in range(train_end_at_d+1, data_end_d+1):
    fin_filename = "%s/data_%din%d.dat"%(data_dirpath,d,data_end_d)
    pg.write("raading %s..."%fin_filename)
    with open(fin_filename) as fin:
        for line in fin:
            u,i,r,t = map(int,line.split())
            if (u,i,r,t) not in ratings_train:
                ratings_test.append((u,i,r,t))

pg.write("writing %s..."%test_filename)
with open(test_filename, "w") as fout:
    for u,i,r in ratings_test:
        fout.write("%d\t%d\t%d\n"%(u,i,r))

pg.write("done", br=True)

