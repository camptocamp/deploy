import logging
logger = logging.getLogger('deploy.remote')

def remote_copy(src, host):
    logger.info("copying '%(src)s' to '%(host)s'"%{'src': src, 'host': host})
    return True

def remote_extract(project, host):
    logger.info("start extracting '%(project)s' at '%(host)s'"%{'project': project, 'host': host})
    return True
