def write(msg, br=False):
    import sys
    sys.stderr.write("\r%s\033[K"%(msg) + ("\n" if br else ""))
    sys.stderr.flush()

