################################
### EVALUATION @Shih Ting Yi ###
################################

from __future__ import division
import sys, os, numpy
from collections import defaultdict
from lib import *
_,data_dirpath,train_end_at_d,data_end_d,train_lang,train_prog,augment_lang,augment_prog,k,locks = sys.argv
_lock_setData,_lock_train,_lock_predict,_lock_recommend,_lock_examine = map(lambda b:b=='1',list(locks))
train_end_at_d,data_end_d,k = int(train_end_at_d),int(data_end_d),int(k)

def read_data_at(d):
    ratings = []
    fin_filename = gen_path(data_dirpath, gen_data_filename(d,data_end_d))
    with open(fin_filename) as fin:
        progress("raading %s..."%fin_filename)
        for line in fin:
            u,i,r,t = map(int,line.split())
            ratings.append((u,i,r,t))
    progress("%d ratings at %d"%(len(ratings),d),br=True)
    return ratings

def read_train_ratings_at(d):
    ratings = []
    fin_filename = gen_data_filename(d, data_end_d, "train")
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r,t = map(int,line.split())
            ratings.append((u,i,r,t))
    progress("%d training ratings at %d"%(len(ratings),d),br=True)
    return ratings

def read_test_ratings_at(d):
    ratings = []
    fin_filename = gen_data_filename(d, data_end_d, "test")
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r,t = map(int,line.split())
            ratings.append((u,i,r,t))
    progress("%d testing ratings at %d"%(len(ratings),d),br=True)
    return ratings

def read_candidates_at(d):
    candidates = []
    fin_filename = gen_data_filename(d, data_end_d, "train.candidates")
    with open(fin_filename) in fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i = map(int,line.split())
            candidates.append((u,i))
    progress("%d candidates at %d"%(len(candidates),d),br=True)
    return candidates

def read_exposure_at(d):
    exposure = {}
    fin_filename = gen_data_filename(d, data_end_d, "train.exposure")
    with open(fin_filename) in fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            i,x = map(int,line.split(':'))
            exposure[i] = x
    return exposure

def read_recommend_at(d):
    recomm_items_of = {}
    fin_filename = gen_data_filename(d, data_end_d, "train.model.predict.recommend")
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,iis = line.split(':')
            u,iis = int(u), map(int,iis.split())
            recomm_items_of[u] = iis
    progress("%d recommendations at %d"%sum(map(len,recomm_items_of.values())),br=True)
    return recomm_items_of

def read_passed_ratings_at(d):
    ratings = []
    fin_filename = gen_data_filename(d, data_end_d, "train.model.predict.recommend.passed")
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r,t = map(int,line.split())
            ratings.append((u,i,r,t))
    progress("%d testing ratings at %d"%(len(ratings),d),br=True)
    return ratings

def read_users():
    fin_filename = gen_path(data_dirpath, "users.dat")
    progress("reading %s..."%fin_filename)
    users = []
    with open(fin_filename) as fin:
        for line in fin:
            u = int(line)
            users.append(u)
    progress("%d users"%len(users),br=True)
    return users

def read_items():
    fin_filename = gen_path(data_dirpath, "items.dat")
    progress("reading %s..."%fin_filename)
    items = []
    with open(fin_filename) as fin:
        for line in fin:
            i = int(line)
            items.append(i)
    progress("%d items"%len(items),br=True)
    return items

def read_model_at(d):
    fin_filename = gen_data_filename(d, data_end_d, "train.model")
    progress("reading %s..."%fin_filename)
    U,I = dict(),dict()
    with open(model_filename) as fin:
        ### read U nRows & nCols
        line = fin.readline()
        nUsers,K = map(int,line.split())
        progress("size(U) = %d x %d"%(nUsers,K), br=True)
    
        ### read U
        for j in range(nUsers):
            line = fin.readline()
            u,vec = line.split(':')
            u,vec = int(u), numpy.array(map(float,vec.split()))
            assert len(vec)==K
            U[u] = vec
    
        ### read I nRows & nCols
        line = fin.readline()
        nItems,K_ = map(int,line.split())
        assert K_==K # dimension of U,I should be identical
        progress("size(I) = %d x %d"%(nItems,K), br=True)
    
        ### read I
        for j in range(nItems):
            line = fin.readline()
            i,vec = line.split(':')
            i,vec = int(i), numpy.array(map(float,vec.split()))
            assert len(vec)==K
            I[i] = vec
    return U,I

##### DATA-SETTING PHASE #####
train_filename = gen_data_filename(train_end_at_d, data_end_d, "train")
test_filename  = gen_data_filename(train_end_at_d, data_end_d, "test")
if _lock_setData:
    progress("setting data...",br=True)

    # set training data
    train_ratings = []

    if train_end_at_d!= 1: # skip this step when the first data division
        # add previous training data
        train_ratings.extend( read_train_ratings_at(train_end_at_d-1) )
        # add previous predicted ratings
        train_ratings.extend( read_passed_ratings_at(train_end_at_d-1) )
    
    # read data of this time division
    ratings_at_d = read_data_at(train_end_at_d)
    for u,i,r,t in ratings_at_d:
        if (u,i,r,t) not in train_ratings: # don't add if the item already included
            train_ratings.append((u,i,r,t)) # add to training data
    
    progress("%d training ratings"%len(train_ratings), br=True)

    # write training data
    fout_filename = train_filename
    with open(fout_filename, "w") as fout:
        progress("writing %s..."%fout_filename)
        for u,i,r,t in train_ratings:
            fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))
    
    # set testing data
    test_ratings = []
    
    # read following data divisions
    for d in range(train_end_at_d+1, data_end_d+1):
        ratings_at_d = read_data_at(d)
        for u,i,r,t in ratings_at_d:
            if (u,i,r,t) not in train_ratings: # don't add if the item already included in training data
                test_ratings.append((u,i,r,t)) # add to testing data
    
    progress("%d testing ratings"%len(test_ratings), br=True)
    
    # write testing data
    fout_filename = test_filename
    with open(fout_filename, "w") as fout:
        progress("writing %s..."%fout_filename)
        for u,i,r,t in test_ratings:
            fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))

    progress("data-setting done!", br=True)

##### TRAINING PHASE #####
model_filename = "%s.model"%train_filename
if _lock_train:
    progress("training...",br=True)

    # train
    progress("training...")
    users_filename = gen_path(data_dirpath, "users.dat")
    items_filename = gen_path(data_dirpath, "items.dat")
    arg = [
        train_filename,
        users_filename,
        items_filename,
        model_filename
    ]
    os.system(gen_cmd(train_lang, train_prog, arg))

    progress("training done!", br=True)

##### PREDICTING PHASE #####
candidates_filename = "%s.candidates"%train_filename
exposure_filename = "%s.exposure"%train_filename
clicked_filename = "%s.clicked"%train_filename
predict_filename = "%s.predict"%model_filename
if _lock_predict:
    progress("predicting...",br=True)

    try:
        train_ratings,test_ratings
    except NameError:
        train_ratings = read_train_ratings_at(train_end_at_d)
        test_ratings = read_test_ratings_at(train_end_at_d)
    try:
        users, items
    except NameError:
        users = read_users()
        items = read_items()
    
    # candidates to recommend
    unrated = set([(u,i) for u in users for i in items])
    rated = set([(u,i) for u,i,r,t in train_ratings])
    unrated -= rated
    candidates = list(unrated)

    progress("%d candidates"%len(candidates),br=True)
    
    # write candidates
    fout_filename = candidates_filename
    with open(fout_filename, "w") as fout:
        progress("writing %s..."%fout_filename)
        for u,i in candidates:
            fout.write("%d %d\n"%(u,i))

    # item exposure
    exposure = {i:0 for i in items}
    for u,i,r,t in train_ratings:
        exposure[i] += 1

    # write item exposure
    fout_filename = exposure_filename
    with open(fout_filename, "w") as fout:
        progress("writing %s..."%fout_filename)
        for i in exposure:
            fout.write("%d:%d\n"%(i,exposure[i]))

    # write clicked pairs
    fout_filename = clicked_filename
    with open(fout_filename, "w") as fout:
        progress("writing %s..."%fout_filename)
        for u,i,r,t in train_ratings:
            fout.write("%d %d\n"%(u,i))

    # RMSE
    U,I = read_model_at(train_end_at_d)
    rmse = 0
    for u,i,r,t in test_ratings:
        r_ = numpy.dot(U[u],I[i])
        rmse += (r - r_)**2
    rmse /= len(test_ratings)
    rmse **= 1/2
    progress("model has RMSE=%.2f"%rmse,br=True)

    # predict
    progress("predicting...")
    arg = [
            candidates_filename,
            model_filename,
            exposure_filename,
            clicked_filename,
            predict_filename
            ]
    os.system(gen_cmd(augment_lang, augment_prog, arg))
    
    progress("predicting done!", br=True)

##### RECOMMENDING PHASE #####
recommend_filename = "%s.recommend"%predict_filename
if _lock_recommend:
    progress("recommending...",br=True)

    predict_ratings = []
    fin_filename = predict_filename
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r_ = line.split()
            u,i,r_ = int(u),int(i),float(r_)
            predict_ratings.append((u,i,r_))

    progress("%d predicted ratings at %d"%(len(predict_ratings),train_end_at_d),br=True)

    # candidate items (& predicted ratings) for each user
    progress("candidate items for each user...")
    u_predict_ratings = defaultdict(list)
    for u,i,r_ in predict_ratings:
        u_predict_ratings[u].append((i,r_))
    
    # recommend
    recomm_items_of = {}
    for u,xs in u_predict_ratings.iteritems():
        recomm_items = sorted(xs, key=lambda (i,r_):r_, reverse=True) # sort by predicted ratings
        recomm_items = recomm_items[:k] # pick top-K
        recomm_items = map(lambda (i,_r):i, recomm_items) # discard predicted ratings
        recomm_items_of[u] = recomm_items

    # write recommendation
    fout_filename = recommend_filename
    with open(fout_filename, "w") as fout:
        progress("writing %s..."%fout_filename)
        for u in recomm_items_of:
            fout.write("%d:%s\n"%(u," ".join(map(str, recomm_items_of[u]))))
    
    progress("recommending done!", br=True)

##### EXAMINING PHASE #####
passed_filename = "%s.passed"%recommend_filename
if _lock_examine:
    progress("examining...",br=True)
   
    try:
        recomm_items_of,test_ratings
    except NameError:
        recomm_items_of = read_recommend_at(train_end_at_d)
        test_ratings = read_test_ratings_at(train_end_at_d)

    # convert test ratings (in u,i)
    progress("processing...")
    future_ratings = {}
    for u,i,r,t in test_ratings:
        future_ratings[u,i] = (u,i,r,t)
    
    # find recommended items that hit
    progress("find recommended items that hit...")
    passed_ratings = []
    for u in recomm_items_of:
        for i in recomm_items_of[u]:
            if (u,i) in future_ratings:
                u,i,r,t = future_ratings[u,i]
                passed_ratings.append((u,i,r,t))

    progress("%d ratings hit"%len(passed_ratings),br=True)

    # write recommendation that hits
    fout_filename = passed_filename
    with open(fout_filename, "w") as fout:
        progress("writing %s..."%fout_filename)
        for u,i,r,t in passed_ratings:
            fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))
    
    progress("examining done!", br=True)
    
