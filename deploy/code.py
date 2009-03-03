def dump(config, savedir):
    print "code: copy '%(src)s' to '%(dest)s'" % {'src': config['dir'], 
                                                  'dest': savedir}
    
def restore(config):
    pass
