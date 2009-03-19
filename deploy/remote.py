from deploy.common import * 
import subprocess, logging

logger = logging.getLogger('deploy.remote')

def remote_copy(src, host):
    cmd = "rsync -az %(srcdir)s %(host)s:%(dstdir)s"% {'srcdir': src, 
                                                        'dstdir': dirname(src),
                                                        'host': host}
    logger.info("running '%(cmd)s' "%{'cmd': cmd})
    p = subprocess.Popen(cmd, shell=True)
    return p.wait() == 0

def remote_extract(dir, host):
    cmd = "ssh %(host)s deploy -x %(dir)s" % {'host': host, 'dir': dir}
    logger.info("running '%(cmd)s'"%{'cmd': cmd})

    p = subprocess.Popen(cmd, shell=True)
    return p.wait() == 0
