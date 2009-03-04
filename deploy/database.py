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

        p = subprocess.Popen(cmd, stdout=output, stderr=errors)
        exitcode = p.wait()

        output.close()
        errors.close()

        if exitcode != 0:
            logger.error("dump error, see '%(errors)s'" %{'errors': errors.name})
            os.remove(output.name)
            sys.exit(1)
        else:
            os.remove(errors.name)

def drop_database(name):
    errors = tempfile.NamedTemporaryFile()

    cmd = ['dropdb', name]
    drop = subprocess.Popen(cmd, stderr=errors)
    exitcode = drop.wait()
    errors.close()
    if exitcode != 0:
        logger.error("drop error, see '%(errors)s'" %{'errors': errors.name})
        sys.exit(1)
    else:
        logger.info("'%(name)s' droped with '%(cmd)s'" %{'name': name, 'cmd': ' '.join(cmd)})
    
    ##drop = 'DROP DATABASE %(name)s;' %{'name': name}
    
def restore(config, srcdir):
    # FIXME: go to maintenance mode: kill connection, restrict to local connections only
    # FIXME: table only restore
    
    restore = config['restore'].split()
    psql = config['psql'].split()
    for name in get_databases(config):
        dumpfile = os.path.join(srcdir, name + '.dump')
        if not os.path.isfile(dumpfile):
            logger.warning("'%(dumpfile)s' not found, database '%(name)' not restored" %{'name': name, 'dumpfile': dumpfile})
        else:
            #drop_database(name)
            cmd = restore + [dumpfile]

            # try to restore the database
            restore_p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            psql_p = subprocess.Popen(psql, stdin=restore_p.stdout)
            psql_p.communicate()
            
            restore_exiitcode = restore_p.wait()
            psql_exiitcode = psql_p.wait()

#             logger.info("restoring '%(name)s' from '%(dumpfile)s'" %{'name': name, 'dumpfile': dumpfile})
#             logger.debug("'%(name)s' restored with '%(cmd)s'" %{'name': name, 'cmd': ' '.join(cmd)})
        
    # FIXME: quit maintenance mode

    ## restore complete database
    # dropdb %(name)s
    # pg_restore -Fc -C -d %(name)s %(dump)s

    ## restore a single table
    # pg_restore -Fc -t foo -d %(name)s %(dump)s
