from deploy.common import * 
import os, sys, logging
logger = logging.getLogger('deploy.apache')

__all__ = ['restore']

def restore(config, codedir):
    if 'active' in config and config['active'] in ('false', 'off', '0'):
        return
    
    if not os.path.exists(os.path.dirname(config['dest'])):
        logger.error("'%(dir)s' do not exists" %{'dir': config['dest']})
        sys.exit(1)

    run_hook('pre-restore-apache', logger=logger)
    f = file(config['dest'], 'w')
    if 'content' not in config:
        f.write("Include %(codedir)s/%(project)s/apache/*.conf\n"%{'codedir': os.path.normpath(codedir),
                                                                   'project': config['project']})
    else:
        f.write(config['content'])

    f.close()
    
    run_hook('post-restore-apache', logger=logger)
    
