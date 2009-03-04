from deploy.common import * 
import os, sys, logging
logger = logging.getLogger('files')

__all__ = ['dump', 'restore']

def dump(config, savedir, symlink=False):
    dirs = [n.strip() for n in config['dirs'].split(',')]
    for src in dirs:
        if src.startswith('/'):
            dest = os.path.join(savedir, src[1:])
            if src.endswith('/'):
                dest = dest[:-1]
        else:
            logger.error("'%s' is not an absolute path" % src)
            sys.exit(1)
        
        if symlink:
            makedirs_silent(os.path.dirname(dest))
            logger.info("symlink '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})
            symlink_silent(src, dest)
        else:
            logger.error("copy '%(src)s' to '%(dest)s' NOT IMPLEMENTED" %{'src': src, 'dest': dest})
            sys.exit(1)
            #copytree(src, dest, symlinks=True)

def restore(config):
    pass
