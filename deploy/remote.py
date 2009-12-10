from deploy.common import * 
import subprocess, logging

logger = logging.getLogger('deploy.remote')

def remote_copy(src, host):
    cmd = "rsync -az --delete %(srcdir)s %(host)s:%(dstdir)s"% {'srcdir': src, 
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
