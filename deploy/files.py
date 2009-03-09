from deploy.common import * 
import os, sys, logging
logger = logging.getLogger('files')

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
            logger.info("copy '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})
            copytree(src, dest)

def restore(config, srcdir):
    run_hook('pre-restore-files')

    for src in get_dirs(config['dirs']):
        
#         print src
#         print dirname(src)
    
#     for d in os.listdir(srcdir):
#         src = os.path.join(srcdir, d)
#         dest = os.path.join('/', d)

#         logger.info("copy '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})
#         #copytree(src, dest, overwrite=False)

    run_hook('post-restore-files')
