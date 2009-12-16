from deploy.common import *
import subprocess
import os, sys, glob, tempfile, time
import logging
logger = logging.getLogger('deploy.databases')

__all__ = ['dump', 'restore']

def get_tables(str):
    tables = {}

    for table in [i.strip() for i in str.split(',') if i]:
        base_table = table.split('.')
        if len(base_table) == 1:
            # all database tables
            tables[base_table[0]] = []
        elif len(base_table) == 2:
            if base_table[0] not in tables:
                tables[base_table[0]] = []
            tables[base_table[0]].append(base_table[1])
        else:
            logger.error("invalid table format : %s''"%table)
            sys.exit(1)

    return tables

def get_tables_from_dir(srcdir):
    files = [f.replace('.dump', '') for f in os.listdir(srcdir) if f.endswith('.dump')]
    return get_tables(','.join(files))

def dump(config, rawtables, savedir):
    if 'active' in config and config['active'] in ('false', 'off', '0'):
        return

    makedirs_silent(savedir)

    dump = config['dump'].split()
    jobs = []
    for database, tables in get_tables(rawtables or config['names']).iteritems():
        if not tables:
            # database without a table: dump all
            cmd = dump + [database]
            output = file(os.path.join(savedir, database + '.dump'), 'w+b')
            errors = file(os.path.join(savedir, database + '.dump.log'), 'w')

            jobs.append({'cmd' : cmd,
                         'args': {'stdout': output, 'stderr': errors}})
        else:
            for table in tables:
                cmd = dump + ['-a', '-t', table, database]
                output = file(os.path.join(savedir, database + '.' + table + '.dump'), 'w+b')
                errors = file(os.path.join(savedir, database + '.' + table + '.dump.log'), 'w')

                jobs.append({'cmd' : cmd,
                             'args': {'stdout': output, 'stderr': errors}})

    for job in jobs:
        logger.info("dumping ('%(cmd)s') to '%(dest)s'" %{'cmd' : ' '.join(job['cmd']),
                                                          'dest': job['args']['stdout'].name})
        
        p = subprocess.Popen(job['cmd'], **job['args'])
        exitcode = p.wait()
        
        if exitcode != 0:
            logger.error("dump error, see '%(errors)s'" %{'errors': job['args']['stderr'].name})
            sys.exit(1)
        else:
            os.remove(job['args']['stderr'].name)
            

def database_exists(name, psqlcmd=['psql']):
    devnull = tempfile.TemporaryFile()
    exists = subprocess.Popen(psqlcmd.extend([name, '-c', '']), stdout=devnull, stderr=subprocess.STDOUT)
    return exists.wait() == 0

def drop_database(name, dropcmd=['dropdb'], psqlcmd=['psql'], tries=10):
    if database_exists(name, psqlcmd=psqlcmd):
        errors = tempfile.TemporaryFile()
        cmd = dropcmd.append(name)
        logger.debug("dropping '%(name)s' with '%(cmd)s'" %{'name': name, 'cmd': ' '.join(cmd)})
        while tries:
            drop = subprocess.Popen(cmd, stdout=errors, stderr=subprocess.STDOUT)
            exitcode = drop.wait()

            if exitcode != 0:
                tries -= 1
                logger.debug("'%(name)s' drop error, sleeping 5s, %(tries)d tries left" %{'name': name, 'tries': tries})
                time.sleep(5)
            else:
                return True

        errors.flush()
        errors.seek(0)
        logger.error("'%(name)s' drop error:\n%(errors)s" %{'name': name, 'errors': errors.read()})
        sys.exit(1)
    else:
        return False
    
def delete_table(database, table, psqlcmd=['psql']):
    if database_exists(database, psqlcmd=psqlcmd):
        errors = tempfile.TemporaryFile()
        cmd = psqlcmd.extend(['-c', "DELETE FROM %(table)s"%{'table': table}, database])
        logger.debug("deleting '%(database)s.%(table)s' with '%(cmd)s'" %{'table': table, 'database': database,
                                                                          'cmd': ' '.join(cmd)})
        drop = subprocess.Popen(cmd, stdout=errors, stderr=subprocess.STDOUT)
        exitcode = drop.wait()
        if exitcode != 0:
            errors.flush()
            errors.seek(0)
            logger.error("'%(database)s.%(table)s' drop error:\n%(errors)s" %{'table': table, 'database': database,
                                                                              'errors': errors.read()})
            sys.exit(1)
        else:
            return True
    else:
        return False        
            
def restore(config, srcdir):

    if not os.path.exists(srcdir):
        logger.debug("'%(srcdir)s' don't exists, no database to restore" %{'srcdir': srcdir})
        return

    restore = config['restore'].split()
    restore_table = config['restore_table'].split()
    psql = config['psql'].split()
    drop = config['drop'].split()

    run_hook('pre-restore-database', get_tables_from_dir(srcdir).keys(), logger=logger)
    jobs = []
    for database, tables in get_tables_from_dir(srcdir).iteritems():
        if not tables:
            # database without a table: restore all database
            dumpfile = os.path.join(srcdir, database + '.dump')
            drop_database(database, dropcmd=drop, psqlcmd=psql)
            cmd = restore + [dumpfile]
            jobs.append({'cmd': cmd})
            
        else:
            for table in tables:
                dumpfile = os.path.join(srcdir, database + '.' + table + '.dump')
                delete_table(database, table, psqlcmd=psql)
                cmd = restore_table + ['-d', database, dumpfile]
                jobs.append({'cmd': cmd})

    for job in jobs:
        logger.info("restoring with '%(cmd)s'" %{'cmd': ' '.join(job['cmd'])})
        errors = tempfile.TemporaryFile()

        p = subprocess.Popen(job['cmd'], stdout=errors, stderr=subprocess.STDOUT)
        exitcode = p.wait()
        if exitcode != 0:
            errors.flush()
            errors.seek(0)
            logger.error("restore error:\n%(errors)s" %{'errors': errors.read()})

    run_hook('post-restore-database', get_tables_from_dir(srcdir).keys(), logger=logger)
