from deploy.common import * 
import subprocess
import os, sys, glob, tempfile, time
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

def database_exists(name):
    devnull = tempfile.TemporaryFile()
    exists = subprocess.Popen(['psql', name, '-c', ''], stdout=devnull, stderr=subprocess.STDOUT)
    return exists.wait() == 0

def drop_database(name, tries=10):
    if database_exists(name):
        errors = tempfile.TemporaryFile()
        while tries:
            cmd = ['dropdb', name]
            drop = subprocess.Popen(cmd, stdout=errors, stderr=subprocess.STDOUT)
            exitcode = drop.wait()

            if exitcode != 0:
                tries -= 1
                logger.debug("'%(name)s' drop error, sleeping 5s, %(tries)d left" %{'name': name, 'tries': tries})
                time.sleep(5)

            else:
                logger.debug("'%(name)s' droped with '%(cmd)s'" %{'name': name, 'cmd': ' '.join(cmd)})
                return True
            
        errors.flush()
        errors.seek(0)
        logger.error("'%(name)s' drop error:\n%(errors)s" %{'name': name, 'errors': errors.read()})
        sys.exit(1)
        
        
def restore(config, srcdir):
    # FIXME: table only restore    
    restore = config['restore'].split()
    psql = config['psql'].split()

    run_hook('pre-restore-database')
    for name in get_databases(config):
        dumpfile = os.path.join(srcdir, name + '.dump')
        if not os.path.isfile(dumpfile):
            logger.warning("'%(dumpfile)s' not found, database '%(name)' not restored" %{'name': name, 'dumpfile': dumpfile})
        else:
            drop_database(name)
            
            cmd = restore + [dumpfile]
            errors = tempfile.TemporaryFile()
            logger.info("restoring '%(name)s' from '%(dump)s'" %{'name': name, 'dump': dumpfile})
            restore_p = subprocess.Popen(cmd, stdout=errors, stderr=subprocess.STDOUT)
            restore_exiitcode = restore_p.wait()
            
            if restore_exiitcode != 0:
                errors.flush()
                errors.seek(0)
                logger.error("'%(name)s' restore error" %{'name': name})
                sys.exit(1) # FIXME: run post-restore-database bore leaving ?
                
    run_hook('post-restore-database')
