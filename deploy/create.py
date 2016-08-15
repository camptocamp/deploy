import os
import logging

from deploy.common import makedirs_silent, basename, copytree, ignore_patterns

logger = logging.getLogger('deploy.create')


def create_update_archive(base, config):
    # FIXME: add version ?
    logger.debug("create '%(base)s' directory" % {'base': base})
    makedirs_silent(base)

    configdst = os.path.join(base, 'deploy.cfg')
    logger.debug("writing full config to '%(configdst)s'" % {'configdst': configdst})
    with open(configdst, 'wb') as configfile:
        config.write(configfile)

    return base


def copy_hooks(hooks, dest):
    logger.debug("copy hooks from '%(hooks)s' to '%(dest)s'" % {'hooks': hooks, 'dest': dest})
    copytree(hooks, os.path.join(dest, basename(hooks)), ignore=ignore_patterns('.svn'))
