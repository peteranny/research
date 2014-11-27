/*
 * User-Item Recommendation with Simple Matrix Factorization
 * Optimized Measure: RMSE
 * Method: SGD
 * Author: Jyun-Yu Jiang from National Taiwan University
 * Mail: jyunyu.jiang@gmail.com
 * Written in 2013.06
 */

#include<iostream>
#include<cstdlib>
#include<cstdio>
#include<cstring>
#include<algorithm>
#include<cassert>
#include<vector>
#include"usage.h"
#include"matrix.h"
#include"data.h"
#include"mf.h"
using namespace std;
int main(int argc, const char* argv[]){    
    if( argc < 1 + 1){
        exit_with_usage();
    }    
    char* train_file = NULL;
    char* model_file = NULL;
    Parameter param;
    int train_idx = read_parameter(argc, argv, param);
    train_file = (char*) argv[train_idx];
    if(train_idx!=argc-1){
        model_file = (char*)argv[train_idx+1];
    }
    assert(train_file != NULL);
    fprintf(stderr,"train file = %s\n",train_file);
    if(model_file == NULL){
        model_file = new char[ strlen(train_file) + 10 ];
        sprintf(model_file,"%s.model",train_file);
    }
    fprintf(stderr,"model file = %s\n",model_file);
    Data data;
    data.load( train_file, param );
    data.adjust_by_mean();

    Data subtrain;
    Data validation;
    data.split( subtrain, validation, 1.0 - param.valid_p);

    fprintf(stderr,"mean = %lf\n", subtrain.mean, validation.mean);
    fprintf(stderr,"var = %lf\n", subtrain.var, validation.var);

    Matrix P = Matrix( param.numU, param.K );
    Matrix Q = Matrix( param.K, param.numI );

    fprintf(stderr,"Start validation...\n");
    int iter, min_iter;
    double min_err = 1e+100;

    for(iter = 0;;iter++){
        mf_update( subtrain, P, Q, param );
        double valid_err = mf_test(validation, P, Q, param);
        double train_err = mf_test(subtrain, P, Q, param);
        if(valid_err < min_err){
            min_err = valid_err;
            min_iter = iter;
        }
        fprintf(stderr,"#%d, train_RMSE = %lf, valid_RMSE = %lf (Best RMSE = %lf in #%d)\n",iter,train_err,valid_err,min_iter,min_err);
        if( iter - min_iter > 20 ){
            break;
        }
    }
    fprintf(stderr,"Best iter : %d (RMSE = %lf)\n", min_iter,min_err);
    
    fprintf(stderr,"Start training...\n");
    P.initialize();
    Q.initialize();
    for(int i=0;i<min_iter+1;i++){
        mf_update( data, P, Q, param );
        double train_err = mf_test(data, P, Q, param);
        fprintf(stderr,"#%d, train_RMSE = %lf\n",i,train_err);
    }
    
    fprintf(stderr,"Write Model...\n");
    write_model(P,Q,param,data.mean,data.var,model_file);

    return 0;
}
