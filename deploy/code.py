from deploy.common import * 
import os, sys, logging
logger = logging.getLogger('code')

__all__ = ['dump', 'restore']

def dump(config, savedir, symlink=False):
    src = config['dir']
    makedirs_silent(savedir)
    linkdst = os.path.join(savedir, config['project'])
    if symlink:
        logger.info("symlink '%(src)s' to '%(dest)s'" %{'src': src, 'dest': linkdst})
        symlink_silent(src, linkdst)
    else:
        logger.error("copy '%(src)s' to '%(dest)s' NOT IMPLEMENTED" %{'src': src, 'dest': savedir})
        sys.exit(1)
        
def restore(config):
    pass
