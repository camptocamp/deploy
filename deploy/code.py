from deploy.common import * 
import os, sys, logging
logger = logging.getLogger('deploy.code')

__all__ = ['dump', 'restore']

def dump(config, savedir, symlink=False):
    if 'src' in config:
        src = config['src']
    else:
        src = config['dir']

    makedirs_silent(savedir)
    dest = os.path.join(savedir, config['project'])
    if symlink:
        logger.info("symlink '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})
        symlink_silent(src, dest)
    else:
        logger.info("copy '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})
        copytree(src, dest, symlinks=True)
        
def restore(config, srcdir):
    if 'dest' in config:
        dest = config['dest']
    else:
        dest = config['dir']

    if os.path.exists(srcdir):
        run_hook('pre-restore-code', [config['project'], dest], logger=logger)

        logger.info("deleting '%(dest)s'" %{'dest': dest})
        rmtree_silent(dest)
        os.makedirs(dest)
        
        logger.info("copying '%(src)s' to '%(dest)s'" %{'src': srcdir, 'dest': dest})
        copytree(srcdir, dirname(dest), symlinks=True, keepdst=True)

        run_hook('post-restore-code', [config['project'], dest], logger=logger)
        
        return dest
    else:
        logger.debug("'%(srcdir)s' don't exists, no code to restore" %{'srcdir': srcdir})
        return None
