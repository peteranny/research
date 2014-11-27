#ifndef _MF_H_
#define _MF_H_
#include<iostream>
#include<cstdlib>
#include<cstdio>
#include<cstring>
#include<cmath>
#include<utility>
#include<vector>
#include"usage.h"
#include"matrix.h"
#include"data.h"
using namespace std;

void write_model(Matrix &P, Matrix &Q, Parameter &param, double mean, double var, char* filename){
    FILE* wp = fopen(filename, "w");
    fprintf(wp,"%d %d %d %lf %lf\n",param.K,param.numU,param.numI,mean,var);
    fprintf(wp,"%d %d\n",P.row,P.col);
    for(int i=0;i<P.row;i++){
        for(int j=0;j<P.col;j++)
            fprintf(wp,"%lf ", P.value[i][j]);
        fprintf(wp,"\n");
    }

    fprintf(wp,"%d %d\n",Q.row,Q.col);
    for(int i=0;i<Q.row;i++){
        for(int j=0;j<Q.col;j++)
            fprintf(wp,"%lf ", Q.value[i][j]);
        fprintf(wp,"\n");
    }
    fclose(wp);
}


void load_model(Matrix &P, Matrix &Q, Parameter &param, double *mean, double *var, char* filename){
    FILE* fp = fopen(filename, "r");
    fscanf(fp,"%d%d%d%lf%lf",&param.K,&param.numU,&param.numI, mean,var);
    fscanf(fp,"%d%d",&P.row,&P.col);
    P.create_matrix(P.row, P.col);
    for(int i=0;i<P.row;i++)
        for(int j=0;j<P.col;j++)
            fscanf(fp,"%lf",&P.value[i][j]);

    fscanf(fp,"%d%d",&Q.row,&Q.col);
    Q.create_matrix(Q.row, Q.col);
    for(int i=0;i<Q.row;i++)
        for(int j=0;j<Q.col;j++)
            fscanf(fp,"%lf",&Q.value[i][j]);
    fclose(fp);
}


void mf_update(Data &data_train, Matrix &P, Matrix &Q, Parameter &param){
    double *new_p = new double[param.K];
    double *new_q = new double[param.K];
    for(int i=0;i<data_train.nData;i++){
        int uu = data_train.uid[i];
        int ii = data_train.iid[i];
        double vv = data_train.val[i]; 

        double now = 0.0;
        for(int j=0;j<param.K;j++) now += P.value[uu][j] * Q.value[j][ii];
        
        for(int j=0;j<param.K;j++){
            new_p[j] = P.value[uu][j] - param.learning_rate * ( - ( vv - now ) * Q.value[j][ii] + param.reg_user * P.value[uu][j] );
            new_q[j] = Q.value[j][ii] - param.learning_rate * ( - ( vv - now ) * P.value[uu][j] + param.reg_item * Q.value[j][ii] );
        }
        for(int j=0;j<param.K;j++){
            P.value[uu][j] = new_p[j];
            Q.value[j][ii] = new_q[j];
        }
    }
    delete new_p;
    delete new_q;
}

double mf_test(Data &data_test, Matrix &P, Matrix &Q, Parameter &param){
    double err = 0.0;
    for(int i=0;i<data_test.nData;i++){
        int uu = data_test.uid[i];
        int ii = data_test.iid[i];
        double vv = data_test.val[i] * data_test.var + data_test.mean; 

        double now = 0.0;
        for(int j=0;j<param.K;j++) now += P.value[uu][j] * Q.value[j][ii];
        now = now * data_test.var +  data_test.mean;
        err += (vv - now)*(vv-now);   
    }
    err = sqrt( err / (double)data_test.nData );
    return err;
}

double mf_test_write(Data &data_test, Matrix &P, Matrix &Q, Parameter &param, FILE* fp){
    double err = 0.0;
    for(int i=0;i<data_test.nData;i++){
        int uu = data_test.uid[i];
        int ii = data_test.iid[i];
        double vv = data_test.val[i] * data_test.var + data_test.mean; 

        double now = 0.0;
        for(int j=0;j<param.K;j++) now += P.value[uu][j] * Q.value[j][ii];
        now = now * data_test.var +  data_test.mean;
        err += (vv - now)*(vv-now); 
        fprintf(fp,"%lf\n",now*data_test.var + data_test.mean);
    }
    err = sqrt( err / (double)data_test.nData );
    return err;
}
#endif
