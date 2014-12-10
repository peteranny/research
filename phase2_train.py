import sys,os
_,train_filename,users_filename,items_filename,lang_name,prog_name = sys.argv
from lib import progress

model_filename = "%s.model"%train_filename
os.system("%s %s %s %s %s %s"%(lang_name, prog_name, train_filename, users_filename, items_filename, model_filename))

