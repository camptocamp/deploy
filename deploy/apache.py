from deploy.common import * 
import os, sys, logging
logger = logging.getLogger('deploy.apache')

__all__ = ['restore']

def restore(config):
    if not os.path.exists(os.path.dirname(config['dest'])):
        logger.error("'%(dir)s' do not exists" %{'dir': config['dest']})
        sys.exit(1)
        
    f = file(config['dest'], 'w')
    print f.name
