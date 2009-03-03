from ConfigParser import RawConfigParser, ConfigParser
from os.path import isfile

def parse_config(f):
    # fixme: check if 'f' is ok and is a valid config file
    if not isfile(f):
        raise Exception("'%s' do not exists")

    config = ConfigParser()
    config.read(['/etc/deploy.cfg', f])
    
    return config
