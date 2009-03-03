#!/usr/bin/env python

from optparse import OptionParser
import logging
from ConfigParser import RawConfigParser, ConfigParser

def parse_config(f):
    # fixme: check if 'f' is ok
    config = ConfigParser()
    config.read(['/etc/deploy.cfg', f])
    
    return config
#     create_apache_config(config.get('apache', 'dest'), 
#                          config.get('apache', 'content'))

#     for section in config.sections():
#         print config.items(section)

#     print config.get('apache', 'dest')

if __name__ == '__main__':
    usage = "usage: %prog [OPTIONS...] [FILE]..."
    parser = OptionParser(usage)
    parser.add_option("-c", "--create", 
                      action="store_true", dest="create",
                      help="create a new archive")
    parser.add_option("-x", "--extract", 
                      action="store_true", dest="extract",
                      help="extract files from an archive")
    parser.add_option("--components", 
                      action="store", type="string", dest="components",
                      default="all",
                      help="restrict component to update.")

    parser.add_option("-v", "--verbose", 
                      action="store_true", dest="verbose", default=True,
                      help="make lots of noise [default]")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose",
                      help="be vewwy quiet")

    (options, args) = parser.parse_args()

    if options.create and options.extract:
        parser.error("options -c and -x are mutually exclusive")

    if options.create:
        if len(args) < 1:
            parser.error("missing configuration file")
        else:
            import create
            # ...
    elif options.extract:
        if len(args) < 1:
            parser.error("missing archive")
        else:
            import extract
            # get config file
            f = extract.get_project_config(args[0])
            config = parse_config(f)
            
            # FIXME: sanity checks

            #extract.extract_project(args[0])
            
