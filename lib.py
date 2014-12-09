def progress(msg, br=False):
    import sys
    sys.stderr.write("\r%s\033[K"%(msg) + ("\n" if br else ""))
    sys.stderr.flush()

def gen_path(dirpath, filename, create=False):
    if create:
        import os
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
    return "%s/%s"%(dirpath, filename)

def gen_data_filename(d,end_d,append=""):
    return "data_%d_in_%d.dat%s"%(d,end_d,("" if append=="" else ".%s"%append))

