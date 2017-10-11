import os
import sys
import ConfigParser

from deploy.common import dirname

import logging
logger = logging.getLogger('deploy.config')


def additional(conf):
    config = ConfigParser.ConfigParser()
    # setup 'here' magic variable
    config.set('DEFAULT', 'here', dirname(conf))
    config.read(conf)
    if config.has_option('main', 'include'):
        return config.get('main', 'include')
    else:
        return None


def parse_config(f, rawenv=None):
    globalconf = '/etc/deploy/deploy.cfg'
    localconf = os.path.abspath(f)

    if not os.path.isfile(globalconf):
        logger.error("can't find global configuration file '%s'" % globalconf)
        sys.exit(1)
    if not os.path.isfile(localconf):
        localconf = os.path.join(localconf, 'deploy.cfg')
        if not os.path.isfile(localconf):
            logger.error("can't find project configuration file '%s'" % localconf)
            sys.exit(1)

    # see if we need to include an additional config file
    config_files = filter(None, [globalconf, additional(localconf), localconf])
    logger.debug("configuration files: %s" % [cf for cf in config_files if cf])

    config = ConfigParser.ConfigParser()
    config.read(config_files)
    # setup 'here' magic variable
    config.set('DEFAULT', 'here', dirname(localconf))

    # setup env section
    if not config.has_section('env'):
        config.add_section('env')

    if rawenv:
        env = dict([tuple(i.split('=')) for i in rawenv.split(',')])
        for k, v in env.iteritems():
            config.set('env', k, v)

    return config
