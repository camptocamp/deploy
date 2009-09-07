import os
import shutil
import subprocess
import logging
import fnmatch
from tempfile import TemporaryFile

__all__ = ['run_hook', 'setup_hooks',
           'dirname', 'basename',
           'ignore_patterns',
           'copytree', 'makedirs_silent',
           'symlink_silent', 'rmtree_silent']

_env = None
_hookdir = None
_default_hookdir = '/etc/deploy/hooks'
_verbose = None

def setup_hooks(config, verbose=True):
    global _hookdir, _default_hookdir, _env, _verbose
    _hookdir = config.get('main', 'hookdir')
    
    # only keep the real env variables (remove the default values)
    _env = dict(config.items('env'))
    for k in config.defaults():
        del _env[k]

    # uppercase the keys
    _env = dict([(k.upper(), v) for k, v in _env.iteritems()])
    
    _verbose = verbose
    # return if the project has custom hooks
    return os.path.normpath(_hookdir) != os.path.normpath(_default_hookdir)

def run_hook(name, arguments=[], logger=None):
    global _hookdir, _default_hookdir, _env, _verbose

    if logger is None:
        logger = logging.getLogger('deploy.hook')

    hook = os.path.join(_hookdir, name)
    if not os.path.exists(hook):
        # back to default hook
        hook = os.path.join(_default_hookdir, name)
        
    if os.path.exists(hook):
        stdout = None
        if not _verbose:
            stdout = TemporaryFile()
            
        logger.info("running '%(name)s'" %{'name': hook})
        h = subprocess.Popen(' '.join([hook] + arguments), shell=True, cwd=dirname(hook), env=_env,
                             stderr=subprocess.STDOUT, stdout=stdout)
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

def ignore_patterns(*patterns):
    """Function that can be used as copytree() ignore parameter.                
                                                                                
    Patterns is a sequence of glob-style patterns                               
    that are used to exclude files"""
    def _ignore_patterns(path, names):
        ignored_names = []
        for pattern in patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))
        return set(ignored_names)
    return _ignore_patterns
