def progress(msg, br=False):
    msg = "* %s"%msg
    import sys
    sys.stderr.write("\r%s\033[K"%(msg) + ("\n" if br else ""))
    sys.stderr.flush()

def gen_path(dirpath, filename, create=False):
    if dirpath[-1]=='/' or dirpath[-1]=='\\':
        dirpath = dirpath[:-1]
    if create:
        import os
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
    return "%s/%s"%(dirpath, filename)

def gen_data_filename(d,end_d,append=""):
    return "data_%d_in_%d.dat%s"%(d,end_d,("" if append=="" else ".%s"%append))

def gen_mk_out_filename():
    import sys
    return "%s.out"%sys.argv[0][sys.argv[0].index('_')+1:sys.argv[0].rindex('.')]

def gen_cmd(lang, prog, arg):
    lang_cmds = {
            "python": "%s %s %s"%(lang, prog, " ".join(arg)),
            "matlab": "%s -r \"%s %s;exit\""%(lang, prog, " ".join(arg)),
            }
    try:
        return lang_cmds[lang]
    except KeyError:
        raise Exception(
                "available languages are " + ", ".join(lang_cmds.keys()) +
                ", " + lang + "%s is not included (please contact administrator)"
                )

