from shutil import copytree

def dump(config, savedir):
    dirs = [n.strip() for n in config['dirs'].split(',')]
    for dir in dirs:
        copytree(dir, savedir, symlinks=True)
        ##print "files: copy '%(src)s' to '%(dest)s'" % {'src': dir, 'dest': savedir}

def restore(config):
    pass
