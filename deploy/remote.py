from deploy.common import *
import subprocess, logging
import time, os

logger = logging.getLogger('deploy.remote')

def remote_copy(src, host):
    cmd = "rsync -az --delete %(srcdir)s %(host)s:%(dstdir)s"% {'srcdir': src,
                                                                'dstdir': dirname(src),
                                                                'host': host}
    logger.info("running '%(cmd)s' "%{'cmd': cmd})
    p = subprocess.Popen(cmd, shell=True)
    return p.wait() == 0

def local_copy(src, host):
    cmd = "rsync -az --delete %(host)s:%(srcdir)s %(dstdir)s"% {'srcdir': src,
                                                                'dstdir': dirname(src),
                                                                'host': host}
    logger.info("running '%(cmd)s' "%{'cmd': cmd})
    p = subprocess.Popen(cmd, shell=True)
    return p.wait() == 0

def remote_extract(dir, host, options):
    cmd = "ssh %(host)s deploy "%{'host': host}
    if options.env:
        cmd += "-e %(env)s "%{'env': options.env}
    if not options.timedir:
        cmd += "-k "
    if not options.verbose:
        cmd += "-q "

    cmd += "-x %(dir)s" %{'dir': dir}
    logger.info("running '%(cmd)s'"%{'cmd': cmd})

    p = subprocess.Popen(cmd, shell=True)
    return p.wait() == 0

def remote_create_dir(host, config, packages_dir):
    cmd = "ssh %(host)s mkdir -p "%{'host': host}
    destpath = config.get('DEFAULT', 'project')
    destpath += '_' + str(int(time.time()))
    dir = os.path.join(packages_dir, destpath)
    cmd += dir

    p = subprocess.Popen(cmd, shell=True)
    p.wait()

    return dir

def remote_create_archive(configfile, dir, host, options):
    cmd = "ssh %(host)s deploy "%{'host': host}
    if not options.timedir:
        cmd += "-k "
    if not options.verbose:
        cmd += "-q "

    cmd += "-c %(configfile)s %(dir)s" %{'dir': dir, 'configfile': configfile}
    logger.info("running '%(cmd)s'"%{'cmd': cmd})

    p = subprocess.Popen(cmd, shell=True)
    return p.wait() == 0
