from ConfigParser import RawConfigParser, ConfigParser
from os.path import isfile

def parse_config(f):
    master = '/etc/deploy.cfg'
    if not isfile(f):
        raise Exception("'%s' No such file or directory" % f)
    if not isfile(master):
        raise Exception("'%s' No such file or directory" % master)

    config = ConfigParser()
    config.read([master, f])
    
    return config
