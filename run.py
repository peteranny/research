################################
### EVALUATION @Shih Ting Yi ###
################################

from __future__ import division
import sys, os, numpy
from collections import defaultdict
from lib import *
_,data_dirpath,train_end_at_d,train_lang,train_prog,augment_lang,augment_prog,topK,delta,locks = sys.argv
_lock_setData,_lock_train,_lock_augment,_lock_recommend,_lock_examine = map(lambda b:b=='1',list(locks))
train_end_at_d,topK,delta = int(train_end_at_d),int(topK),float(delta)

fin_filename = gen_path(data_dirpath, "data.analysis")
with open(fin_filename) as fin:
    line = fin.readline()
    data_end_d = len(line.split()) - 2
progress("data_end_d = %d"%data_end_d,br=True)

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
    train_ratings = []
    fin_filename = gen_data_filename(d, data_end_d, "train")
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r,t = map(int,line.split())
            train_ratings.append((u,i,r,t))
    progress("%d training ratings at %d"%(len(train_ratings),d),br=True)
    return train_ratings

def read_test_ratings_at(d):
    test_ratings = []
    fin_filename = gen_data_filename(d, data_end_d, "test")
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r,t = map(int,line.split())
            test_ratings.append((u,i,r,t))
    progress("%d testing ratings at %d"%(len(test_ratings),d),br=True)
    return test_ratings

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
    fin_filename = gen_data_filename(d, data_end_d, "train.candidates.predict.augment.recommend")
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
    fin_filename = gen_data_filename(d, data_end_d, "train.candidates.predict.augment.recommend.passed")
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

##### DATA-SETTING PHASE #####
train_filename = gen_data_filename(train_end_at_d, data_end_d, "train")
test_filename  = gen_data_filename(train_end_at_d, data_end_d, "test")
if _lock_setData:
    progress("setting data...",br=True)

    # set training data
    train_ratings = []

    if train_end_at_d!=0: # skip this step when the first data division
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
    if len(test_ratings)==0:
        progress("The future data is empty at %d"%train_end_at_d, br=True)
        exit(1)
    
    # write testing data
    fout_filename = test_filename
    with open(fout_filename, "w") as fout:
        progress("writing %s..."%fout_filename)
        for u,i,r,t in test_ratings:
            fout.write("%d\t%d\t%d\t%d\n"%(u,i,r,t))

    progress("data-setting done!", br=True)

##### TRAINING PHASE #####
model_filename = "%s.model"%train_filename
candidates_filename = "%s.candidates"%train_filename
predict_filename = "%s.predict"%candidates_filename
if _lock_train:
    progress("training...",br=True)

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
    
    # candidates to predict
    rated = defaultdict(bool)
    for u,i,r,t in train_ratings:
        rated[u,i] = True
    candidates = [(u,i) for u in users for i in items if not rated[u,i]]

    progress("%d candidates"%len(candidates),br=True)
    
    # write candidates
    fout_filename = candidates_filename
    with open(fout_filename, "w") as fout:
        progress("writing %s..."%fout_filename)
        for u,i in candidates:
            fout.write("%d %d\n"%(u,i))

    # train
    progress("training...")
    users_filename = gen_path(data_dirpath, "users.dat")
    items_filename = gen_path(data_dirpath, "items.dat")
    arg = [
        train_filename,
        users_filename,
        items_filename,
        candidates_filename,
        model_filename,
        predict_filename
    ]
    if os.system(gen_cmd(train_lang, train_prog, arg))!=0:
        progress("The following command goes wrong:",br=True)
        print gen_cmd(train_lang, train_prog, arg)
        exit(1)

    # predicted ratings
    predict_ratings = []
    fin_filename = predict_filename
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r = line.split()
            u,i,r = int(u),int(i),float(r)
            predict_ratings.append((u,i,r))
    progress("%d predicted ratings"%(len(predict_ratings)),br=True)

    # RMSE
    ui_predict_ratings = {(u,i):r for u,i,r in predict_ratings}
    rmse = ( sum([(r - ui_predict_ratings[u,i])**2 for u,i,r,t in test_ratings]) \
            /len(test_ratings) )**1/2
    progress("model has RMSE=%.2f"%rmse,br=True)

    progress("training done!", br=True)

##### AUGMENTING PHASE #####
exposure_filename = "%s.exposure"%train_filename
clicked_filename = "%s.clicked"%train_filename
augment_filename = "%s.augment"%predict_filename
if _lock_augment:
    progress("augmenting...",br=True)

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

    # augment
    progress("augmenting...")
    arg = [
            predict_filename,
            model_filename,
            exposure_filename,
            clicked_filename,
            augment_filename,
            "%f"%delta
            ]
    if os.system(gen_cmd(augment_lang, augment_prog, arg))!=0:
        progress("The following command goes wrong:",br=True)
        print gen_cmd(augment_lang, augment_prog, arg)
        exit(1)
    
    progress("augmenting done!", br=True)

##### RECOMMENDING PHASE #####
recommend_filename = "%s.recommend"%augment_filename
if _lock_recommend:
    progress("recommending...",br=True)

    augment_ratings = []
    fin_filename = augment_filename
    with open(fin_filename) as fin:
        progress("reading %s..."%fin_filename)
        for line in fin:
            u,i,r_ = line.split()
            u,i,r_ = int(u),int(i),float(r_)
            augment_ratings.append((u,i,r_))
    progress("%d augmented ratings"%(len(augment_ratings)),br=True)

    # candidate items (& augment ratings) for each user
    progress("candidate items for each user...")
    u_augment_ratings = defaultdict(list)
    for u,i,r_ in augment_ratings:
        u_augment_ratings[u].append((i,r_))
    
    # recommend
    recomm_items_of = {}
    for u,xs in u_augment_ratings.iteritems():
        recomm_items = sorted(xs, key=lambda (i,r_):r_, reverse=True) # sort by augmented ratings
        recomm_items = recomm_items[:topK] # pick top-K
        recomm_items = map(lambda (i,_r):i, recomm_items) # discard augmented ratings
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
    
