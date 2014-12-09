'''
@ Ting-Yi Shih

#Usage Example
from factory import Factory
Factory(source=[1,2,3], filename="factory_out", func=lambda x:str(x), num_workers=1).run()

source: a list/an iterator/a generator of items
filename: output filename
func: function that returns a string as the result of the item
      can take either 1 argument: item, or take 2 arguments: item and fparam
      item: 1 out of source
      fparam(optional): parameters
fparam: parameters to this function shared by all items (None by default)
        if func takes exactly 1 argument, fparam must be None
        if func takes exactly 2 arguments, fparam must not be None
num_worker: number of process to be executed

'''

from __future__ import division

class Factory:
    def __init__(this, source=[], filename="factory_out", func=lambda x:str(x), fparam=None, num_workers=1):
        this.source = source
        this.fout_name = filename
        this.func = func
        this.num_workers = num_workers
        this.fparam = fparam

    @staticmethod
    def worker(worker_id, in_queue, func, fparam, fout): # make args a tuple 
        while True:
            item = in_queue.get()
            result = func(item, fparam) if fparam else func(item) # input=item,args output=string
            fout.write("%s\n"%result)
            fout.flush()
            in_queue.task_done()

    @staticmethod
    def progressor(in_queue,total_num):
        if total_num==0: return
        import time,sys
        while True:
            Factory.pg("%5.1f%%..."%(100-in_queue.qsize()/total_num*100))
            time.sleep(1)

    @staticmethod
    def pg(msg, br=False):
        import sys
        sys.stderr.write("\rFactory: "+msg+"\033[K"+("\n" if br else ""))
        sys.stderr.flush()

    def test(this):
        try:
            this.source = iter(this.source)
        except:
            raise Exception("source should be a iterable")
        import inspect
        if this.fparam is None:
            if len(inspect.getargspec(this.func).args)!=1:
                raise Exception("function should take exactly 1 argument: item")
        if this.fparam is not None:
            if len(inspect.getargspec(this.func).args)!=2:
                raise Exception("function should take exactly 2 arguments:item and parameters")
        if this.fout_name=="":
            raise Exception("filename cannot be an empty string")
        if type(this.num_workers)!=type(1) or this.num_workers<=0:
            raise Exception("invalid value of num_workers")
        try:
            item = next(this.source)
        except:
            raise Exception("source is empty")
        result = this.func(item, this.fparam) if this.fparam else this.func(item)
        if type(result)!=type(""):
            raise Exception("function should return a string")
        with open("%s_part"%this.fout_name, "w") as fout:
            fout.write("%s\n"%result)
            fout.flush()

    def run(this):
        Factory.pg("configuration test...")
        this.test() # check configuration

        source = this.source
        fout_name = this.fout_name
        func = this.func
        fparam = this.fparam
        num_workers = this.num_workers
        worker = this.worker
        progressor = this.progressor

        # queue settings
        Factory.pg("arranging source elements...")
        from multiprocessing import JoinableQueue,Process
        in_queue = JoinableQueue()
        for item in source:
            in_queue.put(item)

        # worker progressing
        progressor = Process(target=progressor, args=(in_queue, in_queue.qsize()))
        import time
        start_time = time.time()
        progressor.start()

        # worker settings 
        fouts, workers = [], []
        for w_id in xrange(num_workers):
            fouts.append(open("%s_part%d"%(fout_name,w_id),"w"))
            workers.append(Process(target=worker, args=(w_id, in_queue, func, fparam, fouts[w_id])))
            workers[w_id].start()

        # post processing
        in_queue.join()
        for w_id in xrange(num_workers):
            workers[w_id].terminate()
        progressor.terminate()
        end_time = time.time()
        Factory.pg("working done (%.1fs lapsed)"%(end_time - start_time), br=True)
        import os
        os.system("cat %s_part* > %s"%(fout_name,fout_name))
        os.system("rm -f %s_part*"%(fout_name))

# useful when the output is not str (not recommended)
def obj2line(obj):
	return str(obj)
def line2obj(line):
	import ast
	return ast.literal_eval(line)

# useful when batch processing (1 result for all instead of for each) (not recommended)
def src2chunk(source, nChunks):
	import math
	source = list(source)
	chunk_size = int(math.ceil(len(source)/nChunks))
	return [source[i:i+chunk_size] for i in xrange(0,len(source),chunk_size)]
def mergeLines(filename, res, update):
	with open(filename, "r") as fin:
		for line in fin:
			res_prt = line2obj(line)
			res = update(res,res_prt)
	with open(filename, "w") as fout:
		fout.write(obj2line(res))

if __name__ == "__main__":
    def simple(x,fparam):
        import time
        time.sleep(fparam)
        return str(x)
    Factory(source=range(10), filename="factory_out", func=simple, fparam=3, num_workers=5).run()

