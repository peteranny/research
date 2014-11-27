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
    if( argc < 1 + 2){
        exit_with_predict_usage();
    }    
    char* test_file = (char*) argv[1];
    char* model_file = (char*) argv[2];
    char* predict_file = NULL;
    if(argc > 1+2){
        predict_file = (char*) argv[3];        
    }else{
        predict_file = new char[ strlen(test_file) + 10 ];
        sprintf(predict_file,"%s.pred",test_file);
    }
    fprintf(stderr,"test file = %s\n",test_file);
    fprintf(stderr,"model file = %s\n",model_file);
    fprintf(stderr,"predict file = %s\n",predict_file);

    Matrix P;
    Matrix Q;
    Parameter param;
    double mean, var;
    load_model(P, Q, param, &mean, &var, model_file);
    Data data;
    data.load_for_test( test_file );
    data.adjust_by_value( mean, var );
    data.mean = mean;
    data.var = var;

    if(predict_file == NULL){
        fprintf(stderr,"Err = %lf\n", mf_test(data, P, Q, param) );
    }else{
        FILE* fp = fopen(predict_file,"w");
        fprintf(stderr,"Err = %lf\n", mf_test_write(data, P, Q, param, fp) );
        fclose(fp);
    }


    return 0;
}
