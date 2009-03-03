import subprocess
from os import makedirs
from os.path import join, isdir
import logging
logger = logging.getLogger('databases')

def dump(config, savedir):
    # FIXME: table only dump
    if not isdir(savedir):
        makedirs(savedir)

    names = [n.strip() for n in config['names'].split(',')]
    dump = config['dump'].split()
    for name in names:
        cmd = dump + [name]
        output = file(join(savedir, name + '.dump'), 'w+b')
        errors = file(join(savedir, name + '.dump.log'), 'w')
        logger.debug("dump '%(src)s' to '%(dest)s'" %{'src': name, 'dest': output.name})

        exitcode = subprocess.call(cmd, stdout=output, stderr=errors)
        output.close()
        errors.close()

        if exitcode != 0:
            logger.error("dump error, see '%(errors)s'" % {'errors': errors.name})
            import sys
            sys.exit(1)

def restore(config, dump):
    ## restore complete database
    # dropdb %(name)s
    # pg_restore -Fc -C -d %(name)s %(dump)s

    ## restore a single table
    # pg_restore -Fc -t foo -d %(name)s %(dump)s
    pass
