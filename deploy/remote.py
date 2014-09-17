import subprocess
import logging
import time
import os

from deploy.common import dirname

logger = logging.getLogger('deploy.remote')


def remote_copy(config, src, host):
    cmd = "rsync %(rsync_args)s %(srcdir)s %(host)s:%(dstdir)s" % {
        'rsync_args': config.get('main', 'rsync_args'),
        'srcdir': src,
        'dstdir': dirname(src),
        'host': host
    }
    logger.info("running '%(cmd)s' " % {'cmd': cmd})
    p = subprocess.Popen(cmd, shell=True)
    return p.wait() == 0


def local_copy(config, src, host):
    cmd = "rsync %(rsync_args)s %(host)s:%(srcdir)s %(dstdir)s" % {
        'rsync_args': config.get('main', 'rsync_args'),
        'srcdir': src,
        'dstdir': dirname(src),
        'host': host
    }
    logger.info("running '%(cmd)s' " % {'cmd': cmd})
    p = subprocess.Popen(cmd, shell=True)
    return p.wait() == 0


def remote_extract(config, dir, host, options):
    cmd = "ssh %(ssh_args)s %(host)s deploy " % {
        'ssh_args': config.get('main', 'ssh_args'),
        'host': host
    }
    if options.env:
        cmd += "-e %(env)s " % {'env': options.env}
    if not options.timedir:
        cmd += "-k "
    if not options.verbose:
        cmd += "-q "

    cmd += "-x %(dir)s" % {'dir': dir}
    logger.info("running '%(cmd)s'" % {'cmd': cmd})

    p = subprocess.Popen(cmd, shell=True)
    return p.wait() == 0


def remote_create_dir(config, host, packages_dir):
    cmd = "ssh %(ssh_args)s %(host)s mkdir -p " % {
        'ssh_args': config.get('main', 'ssh_args'),
        'host': host
    }
    destpath = config.get('DEFAULT', 'project')
    destpath += '_' + str(int(time.time()))
    dir = os.path.join(packages_dir, destpath)
    cmd += dir

    p = subprocess.Popen(cmd, shell=True)
    p.wait()

    return dir


def remote_create_archive(config, configfile, dir, host, options):
    cmd = "ssh %(ssh_args)s %(host)s deploy " % {
        'ssh_args': config.get('main', 'ssh_args'),
        'host': host
    }
    if not options.timedir:
        cmd += "-k "
    if not options.verbose:
        cmd += "-q "
    # if options.tables:
    #     cmd += "--tables "+options.tables+" "

    cmd += "-c %(configfile)s %(dir)s" % {
        'dir': dir,
        'configfile': configfile
    }
    logger.info("running '%(cmd)s'" % {'cmd': cmd})

    p = subprocess.Popen(cmd, shell=True)
    return p.wait() == 0
