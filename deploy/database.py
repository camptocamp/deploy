from deploy.common import * 
import subprocess
import os, sys, glob, tempfile
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

# def database_exists(name):
#     return False

# def drop_database(name):
#     if database_exists(name):
#         errors = tempfile.TemporaryFile()
    
#         cmd = ['dropdb', name]

#         drop = subprocess.Popen(cmd, stdout=errors, stderr=subprocess.STDOUT)
#         exitcode = drop.wait()

#         if exitcode != 0:
#             errors.flush()
#             errors.seek(0)
#             logger.error("'%(name)s' drop error:\n %(errors)s" %{'name': name, 'errors': errors.read()})
#             sys.exit(1)
#         else:
#             logger.info("'%(name)s' droped with '%(cmd)s'" %{'name': name, 'cmd': ' '.join(cmd)})
        
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
            errors = tempfile.TemporaryFile()
            restore_p = subprocess.Popen(cmd, stdout=errors, stderr=subprocess.STDOUT)
            restore_exiitcode = restore_p.wait()
            
            if restore_exiitcode != 0:
                errors.flush()
                errors.seek(0)
                logger.error("'%(name)s' restore error" %{'name': name})
                sys.exit(1)
            else:
                logger.info("'%(name)s' database restored from '%(dump)s'" %{'name': name, 'dump': dumpfile})

#             restore_sql.flush()
#             restore_sql.seek(0)

#             # restore database
#             errors = tempfile.TemporaryFile()
#             psql_p = subprocess.Popen(psql + ['-f', restore_sql.name, 'template1'])
#             #psql_p = subprocess.Popen(psql + ['-f', restore_sql.name, 'template1'], stdout=errors, stderr=subprocess.STDOUT)
#             psql_exiitcode = psql_p.wait()
#             restore_sql.close()
#             print psql_exiitcode
            
#             #######################3
#             errors = tempfile.TemporaryFile()

#             # try to restore the database
#             restore_p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
#             psql_p = subprocess.Popen(psql, stdin=restore_p.stdout, stdout=errors, stderr=subprocess.STDOUT)
#             psql_p.communicate()
            
#             restore_exiitcode = restore_p.wait()
#             psql_exiitcode = psql_p.wait()

#             if restore_exiitcode + psql_exiitcode != 0:
#                 errors.flush()
#                 errors.seek(0)
#                 logger.error("'%(name)s' restore error:\n %(errors)s" %{'name': name, 'errors': errors.read()})
#                 sys.exit(1)
#             else:
#                 logger.info("'%(name)s' database restored from '%(src)s'" %{'name': name, 'dest': dumpfile})
#                 #logger.debug("'%(name)s' restore with '%(errors)s'" %{'name': name, 'errors': errors.read()})
                
#             logger.info("restoring '%(name)s' from '%(dumpfile)s'" %{'name': name, 'dumpfile': dumpfile})
#             logger.debug("'%(name)s' restored with '%(cmd)s'" %{'name': name, 'cmd': ' '.join(cmd)})
        
    # FIXME: quit maintenance mode

    ## restore complete database
    # dropdb %(name)s
    # pg_restore -Fc -C -d %(name)s %(dump)s

    ## restore a single table
    # pg_restore -Fc -t foo -d %(name)s %(dump)s
