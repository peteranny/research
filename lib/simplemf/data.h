#ifndef _DATA_H_
#define _DATA_H_
#include<iostream>
#include<cstdlib>
#include<cstdio>
#include<cmath>
#include<cstring>
#include<cassert>
#include<utility>
#include<vector>
#include<algorithm>
#include"usage.h"
using namespace std;

class Data{
    public:
        int nData, data_length;
        int *uid, *iid;
        double *val;
        double mean,var;
        Data(){
            nData = 0;
            data_length = 1024; 
            uid = (int*) malloc( data_length * sizeof(int) );
            iid = (int*) malloc( data_length * sizeof(int) );
            val = (double*) malloc( data_length * sizeof(double) );
        };
        ~Data(){ if(data_length){ free(uid); free(iid); free(val); } };
        void load(char *filename, Parameter &param);
        void load_for_test(char *filename );
        void insert(int uu, int ii, double vv);
        void adjust_by_mean();
        void adjust_by_value(double vm, double vv);
        void split(Data &data_a, Data &data_b, double percent);
};

void Data::insert(int uu, int ii, double vv){
    if(data_length == nData){
        data_length *= 2;
        int*    new_uid =    (int*) malloc( data_length * sizeof(int) );
        int*    new_iid =    (int*) malloc( data_length * sizeof(int) );
        double* new_val = (double*) malloc( data_length * sizeof(double) );
        for(int i=0;i<nData;i++){
            new_uid[i] = uid[i];
            new_iid[i] = iid[i];
            new_val[i] = val[i];
        }
        free(uid);
        free(iid);
        free(val);
        uid = new_uid;
        iid = new_iid;
        val = new_val;
    }
    uid[nData] = uu;
    iid[nData] = ii;
    val[nData] = vv;
    nData++;
}

void Data::load(char *filename, Parameter &param){
    FILE* fp = fopen(filename, "r");
    int uu, ii;
    double vv;
    int nU = 0, nI = 0;
    while(fscanf(fp,"%d %d %lf",&uu,&ii,&vv)!=EOF){
        insert(uu,ii,vv);
        if( uu > nU ) nU = uu;
        if( ii > nI ) nI = ii;
    }
    fclose(fp);
    if( param.numU == -1 ) param.numU = nU + 1;
    if( param.numI == -1 ) param.numI = nI + 1;
    // random shuffle
    int*    new_uid =    (int*) malloc( data_length * sizeof(int) );
    int*    new_iid =    (int*) malloc( data_length * sizeof(int) );
    double* new_val = (double*) malloc( data_length * sizeof(double) );
    int*    new_idx =    (int*) malloc( nData * sizeof(int) );
    for(int i=0;i<nData;i++) new_idx[i] = i;
    random_shuffle(new_idx, new_idx + nData);
    for(int i=0;i<nData;i++){
        new_uid[i] = uid[ new_idx[i] ];
        new_iid[i] = iid[ new_idx[i] ];
        new_val[i] = val[ new_idx[i] ];
    }
    free(new_idx);
    free(uid);
    free(iid);
    free(val);
    uid = new_uid;
    iid = new_iid;
    val = new_val;
}


void Data::load_for_test(char *filename){
    FILE* fp = fopen(filename, "r");
    int uu, ii;
    double vv;
    while(fscanf(fp,"%d %d %lf",&uu,&ii,&vv)!=EOF){
        insert(uu,ii,vv);
    }
    fclose(fp);
}


void Data::adjust_by_value(double vm, double vv){
    mean = vm;
    var = vv;
    for(int i=0;i<nData;i++){
        val[i] -= vm;
        val[i] /= vv;
    }
}

void Data::adjust_by_mean(){
    mean = 0.0;
    var = 0.0;
    for(int i=0;i<nData;i++){
        mean += val[i];
    }
    mean /= (double) nData;
    for(int i=0;i<nData;i++){
        var += (val[i] - mean) * (val[i] - mean );
    }
    var /= (double) nData;
    var = sqrt(var);

    for(int i=0;i<nData;i++){
        val[i] -= mean;
        val[i] /= var;
    }
}

void Data::split(Data &data_a, Data &data_b, double percent){
    assert(percent<=1.0);

    data_a.mean = data_b.mean = mean;
    data_a.var = data_b.var = var;
    
    int L = (int)( ((double)nData) * percent );
    int w = 0;
    for(;w<L;w++){
        data_a.insert( uid[w], iid[w], val[w]);
    }
    for(;w<nData;w++){
        data_b.insert( uid[w], iid[w], val[w]);
    }

}

#endif
