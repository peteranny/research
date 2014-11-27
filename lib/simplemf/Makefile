all:
	g++ -mcmodel=large -O2 -o simplemf matrix.h usage.h data.h mf.h simplemf.cpp 
	g++ -mcmodel=large -O2 -o simplemf-predict matrix.h usage.h data.h mf.h simplemf-predict.cpp 
clean:
	rm simplemf simplemf-predict
