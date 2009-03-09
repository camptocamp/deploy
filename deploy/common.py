import os, shutil, subprocess
import logging

__all__ = ['run_hook',
           'copytree', 'makedirs_silent',
           'symlink_silent', 'rmtree_silent']

def run_hook(name, arguments=''):
    logger = logging.getLogger('hook')
    
    hookdir = '/etc/deploy/hooks'
    hook = os.path.join(hookdir, name)
    if os.path.exists(hook):
        logger.debug("running '%(name)s'" %{'name': hook})
        h = subprocess.Popen(hook + arguments, shell=True)
        exitcode = h.wait()
        # FIXME: check exitcode
        
def rmtree_silent(path, ignore_errors=False, onerror=None):
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors, onerror)
        
def symlink_silent(src, dst):
    if not os.path.exists(dst):
        os.symlink(src, dst)

def makedirs_silent(name, mode=0777):
    if not os.path.exists(name):
        os.makedirs(name, mode)
    
def copytree(src, dst, symlinks=False, ignore=None):
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
        
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
                copytree(srcname, dstname, symlinks, ignore)
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
        errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error, errors

