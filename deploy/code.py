from deploy.common import * 
import os, sys, logging
logger = logging.getLogger('code')

def dump(config, savedir):
    src = config['dir']
    logger.debug("copy '%(src)s' to '%(dest)s'" %{'src': src, 'dest': savedir})
    # FIXME: ignore .svn ?
    copytree(src, savedir, symlinks=True)

def restore(config):
    pass
