import ConfigParser
import os, sys
import logging
logger = logging.getLogger('deploy.config')

def parse_config(f):
    globalconf = '/etc/deploy.cfg'
    localconf = f
    
    if not os.path.isfile(globalconf):
        logger.error("can't find global configuration file '%s'" % globalconf)
        sys.exit(1)
    if not os.path.isfile(localconf):
        localconf = os.path.join(localconf, 'deploy.cfg') 
        if not os.path.isfile(localconf):
            logger.error("can't find project configuration file '%s'" % localconf)
            sys.exit(1)

    logger.debug("using '%(globalconf)s' and '%(localconf)s'" % {'globalconf': globalconf,
                                                                 'localconf': localconf})
    config = ConfigParser.ConfigParser()
    config.read([globalconf, localconf])
    
    return config

# def get_archive():
#     pass
