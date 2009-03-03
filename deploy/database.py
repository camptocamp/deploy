import subprocess
from os.path import join

def dump(config, savedir):
    # FIXME: table only dump
    names = [n.strip() for n in config['names'].split(',')]
    dump = config['dump'].split()
    for name in names:
        cmd = dump + [name]
        output = file(join(savedir, name + '.dump'), 'w+b')
        subprocess.call(cmd, stdout=output)
        output.close()

def restore(config, dump):
    ## restore complete database
    # dropdb %(name)s
    # pg_restore -Fc -C -d %(name)s %(dump)s

    ## restore a single table
    # pg_restore -Fc -t foo -d %(name)s %(dump)s
    pass
