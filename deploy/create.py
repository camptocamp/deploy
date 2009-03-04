from deploy.common import * 
import os, shutil
import logging
logger = logging.getLogger('create')

def create_update_archive(base, configfile):
    # FIXME: add version ?
    logger.debug("create '%(base)s' directory" %{'base': base})
    makedirs_silent(base)

    configdst = os.path.join(base, 'deploy.cfg')
    logger.debug("copy '%(confsrc)s' to '%(configdst)s'" %{'confsrc': configfile, 'configdst': configdst})
    shutil.copy(configfile, configdst)
    return base
