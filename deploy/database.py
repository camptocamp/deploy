from deploy.common import * 
import subprocess
import os, sys, glob
import logging
logger = logging.getLogger('databases')

__all__ = ['dump', 'restore']

def get_databases(config):
    return [n.strip() for n in config['names'].split(',')]

def dump(config, savedir):
    # FIXME: table only dump
    makedirs_silent(savedir)

    dump = config['dump'].split()
    for name in get_databases(config):
        cmd = dump + [name]
        output = file(os.path.join(savedir, name + '.dump'), 'w+b')
        errors = file(os.path.join(savedir, name + '.dump.log'), 'w')
        logger.info("dump '%(name)s' database to '%(dest)s'" %{'name': name, 'dest': output.name})
        logger.debug("'%(name)s' dumped with '%(cmd)s'" %{'name': name, 'cmd': ' '.join(cmd)})

        exitcode = subprocess.call(cmd, stdout=output, stderr=errors)
        output.close()
        errors.close()

        if exitcode != 0:
            logger.error("dump error, see '%(errors)s'" %{'errors': errors.name})
            os.remove(output.name)
            sys.exit(1)
        else:
            os.remove(errors.name)
            
def restore(config, srcdir):
    # FIXME: go to maintenance mode: kill connection, restrict to local connections only
    restore = config['restore'].split()
    
    for name in get_databases(config):
        dumpfile = os.path.join(srcdir, name + '.dump')
        if not os.path.isfile(dumpfile):
            logger.debug("'%(dumpfile)s' not found, database '%(name)' not restored" %{'name': name, 'dumpfile': dumpfile})
            continue

        drop = 'DROP DATABASE %(name)s;' %{'name': name}
        
        cmd = restore + [dumpfile]
        logger.info("restoring '%(name)s' from '%(dumpfile)s'" %{'name': name, 'dumpfile': dumpfile})
        logger.debug("'%(name)s' restored with '%(cmd)s'" %{'name': name, 'cmd': ' '.join(cmd)})
        
    # FIXME: quit maintenance mode

    ## restore complete database
    # dropdb %(name)s
    # pg_restore -Fc -C -d %(name)s %(dump)s

    ## restore a single table
    # pg_restore -Fc -t foo -d %(name)s %(dump)s
