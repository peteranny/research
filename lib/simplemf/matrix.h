#ifndef _MATRIX_H_
#define _MATRIX_H_
#include<iostream>
#include<cstdlib>
#include<cstdio>
#include<cstring>
#include<algorithm>
#include"usage.h"
using namespace std;
class Matrix;

class Matrix{
    public:
        int row, col;
        double** value;
        Matrix(){ row = col = 0; value = NULL; };
        Matrix(int r, int c);
        ~Matrix(){ if(value!=NULL) delete_2d_double_array(value,row,col); };
        Matrix(const Matrix &);
        void create_matrix(int r, int c);
        void initialize();
        void print();
};

Matrix::Matrix(int r, int c){
    value = NULL;
    create_matrix(r,c);
}

Matrix::Matrix(const Matrix &mat){
    row = mat.row;
    col = mat.col;
    create_matrix(row, col);
    for(int i=0;i<row;i++) for(int j=0;j<col;j++){
        value[i][j] = mat.value[i][j];
    }
}

void Matrix::create_matrix(int r, int c){
    if(value != NULL){
        delete_2d_double_array(value, r,c);
    }
    row = r;
    col = c;
    value = create_2d_double_array(row, col);
    initialize();
}


void Matrix::initialize(){
    for(int i=0;i<row;i++) for(int j=0;j<col;j++){
        value[i][j] = double( (rand()%200001) - 100000 ) / 100000.0;        
    }
}
void Matrix::print(){
    for(int i=0;i<row;i++){
        for(int j=0;j<col;j++) fprintf(stderr,"%.5lf ", value[i][j]);
        fprintf(stderr,"\n");
    }

}
#endif
