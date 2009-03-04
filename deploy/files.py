from deploy.common import * 
import os, sys, logging
logger = logging.getLogger('files')

def dump(config, savedir):
    dirs = [n.strip() for n in config['dirs'].split(',')]
    for src in dirs:
        if src.startswith('/'):
            dest = os.path.join(savedir, src[1:])
        else:
            logger.error("'%s' is not an absolute path" % src)
            sys.exit(1)
            
        logger.debug("copy '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})
        #copytree(src, dest, symlinks=True)
        ##print "files: copy '%(src)s' to '%(dest)s'" % {'src': dir, 'dest': savedir}

def restore(config):
    pass
