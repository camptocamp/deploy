from deploy.common import * 
import os, logging
logger = logging.getLogger('deploy.code')

__all__ = ['dump', 'restore']

def dump(config, savedir, symlink=False):
    if 'active' in config and config['active'] in ('false', 'off', '0'):
        return

    if 'src' in config:
        src = config['src']
    else:
        src = config['dir']

    if 'ignore' in config:
        ignore = ignore_patterns(*[p.strip() for p in config['ignore'].split(',')])
    else:
        ignore = None

    run_hook('pre-create-code', [config['project'], src], logger=logger, exit_on_error=True)

    makedirs_silent(savedir)
    dest = os.path.join(savedir, config['project'])
    if symlink:
        logger.info("symlink '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})
        symlink_silent(src, dest)
    else:
        logger.info("copy '%(src)s' to '%(dest)s'" %{'src': src, 'dest': dest})
        copytree(src, dest, symlinks=True, ignore=ignore)

    run_hook('post-create-code', [config['project'], src], logger=logger)
        
def restore(config, srcdir):
    if 'dest' in config:
        dest = config['dest']
    else:
        dest = config['dir']

    srcdir = os.path.join(srcdir, config['project'])
    if os.path.exists(srcdir):
        run_hook('pre-restore-code', [config['project'], dest], logger=logger)

        logger.info("deleting '%(dest)s'" %{'dest': dest})
        rmtree_silent(dest)
        os.makedirs(dest)
        
        logger.info("copying '%(src)s' to '%(dest)s'" %{'src': srcdir, 'dest': dest})
        copytree(srcdir, dest, symlinks=True, keepdst=True)

        run_hook('post-restore-code', [config['project'], dest], logger=logger)
        
        return dest
    else:
        logger.debug("'%(srcdir)s' don't exists, no code to restore" %{'srcdir': srcdir})
        return None
