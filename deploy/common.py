import os, shutil, subprocess, logging

__all__ = ['run_hook', 'dirname', 'basename',
           'copytree', 'makedirs_silent',
           'symlink_silent', 'rmtree_silent']

def run_hook(name, arguments=[], logger=None):
    if logger is None:
        logger = logging.getLogger('deploy.hook')
        
    hookdir = '/etc/deploy/hooks'
    hook = os.path.join(hookdir, name)
    if os.path.exists(hook):
        logger.debug("running '%(name)s'" %{'name': hook})
        h = subprocess.Popen(' '.join([hook] + arguments), shell=True)
        exitcode = h.wait()

        return exitcode == 0
    else:
        return True

def basename(path):
    if path.endswith('/'):
        return os.path.basename(path[:-1])
    else:
        return os.path.basename(path)

def dirname(path):
    if path.endswith('/'):
        return os.path.dirname(path[:-1])
    else:
        return os.path.dirname(path)

def rmtree_silent(path, ignore_errors=False, onerror=None):
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors, onerror)
        
def symlink_silent(src, dst):
    if not os.path.exists(dst):
        os.symlink(src, dst)

def makedirs_silent(name, mode=0777):
    if not os.path.exists(name):
        os.makedirs(name, mode)
    
def copytree(src, dst, symlinks=False, ignore=None, keepdst=False):
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not keepdst and os.path.exists(dst):
        shutil.rmtree(dst)
    makedirs_silent(dst)

    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore, keepdst)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        # don't care about permission errors
        #errors.extend((src, dst, str(why)))
        pass
    if errors:
        raise shutil.Error, errors

