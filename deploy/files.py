from deploy.common import * 
import os, sys, logging
logger = logging.getLogger('deploy.files')

__all__ = ['dump', 'restore']

def get_dirs(str):
    return [n.strip() for n in str.split(',')]

def dump(config, savedir, symlink=False):
    for src in get_dirs(config['dirs']):
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
            logger.info("copying '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})
            copytree(src, dest)

def restore(config, srcdir):
    run_hook('pre-restore-files', logger=logger)

    for dest in get_dirs(config['dirs']):
        logger.info("deleting '%(dest)s'" %{'dest': dest})
        rmtree_silent(dest)
        
        # first '/' removed in second arg
        src = os.path.join(srcdir, dest[1:])

        logger.info("copying '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})
        copytree(src, dest)

    run_hook('post-restore-files', logger=logger)
