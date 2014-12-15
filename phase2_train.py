### phase2_train

import sys,os
_,train_filename,users_filename,items_filename,lang_name,prog_name = sys.argv
from lib import progress

progress("training...")
model_filename = "%s.model"%train_filename
os.system("%s %s %s %s %s %s"%(
    lang_name,
    prog_name,
    train_filename, ### argv[1]
    users_filename, ### argv[2]
    items_filename, ### argv[3]
    model_filename  ### argv[4]
    ))

progress("done", br=True)

