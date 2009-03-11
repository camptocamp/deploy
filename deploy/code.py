from deploy.common import * 
import os, sys, logging
logger = logging.getLogger('code')

__all__ = ['dump', 'restore']

def dump(config, savedir, symlink=False):
    src = config['dir']
    makedirs_silent(savedir)
    dest = os.path.join(savedir, config['project'])
    if symlink:
        logger.info("symlink '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})
        symlink_silent(src, dest)
    else:
        logger.info("copy '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})
        copytree(src, dest)
        
def restore(config, srcdir):
    dest = config['dir']
    # FIXME: assert destdir exists
    run_hook('pre-restore-code')

    logger.info("deleting '%(dest)s'" %{'dest': dest})
    ###rmtree_silent(dest)

    src = srcdir
    logger.info("copying '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})

    run_hook('post-restore-code')
