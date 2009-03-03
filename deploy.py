#!/usr/bin/env python

from optparse import OptionParser
import logging

from deploy.config import *

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
    if not options.create and not options.extract:
        parser.error("missing action")
    
    if options.create:
        if len(args) < 1:
            parser.error("missing configuration file")
        else:
            from  deploy import create
            config = parse_config(args[0])
            # ...
    elif options.extract:
        if len(args) < 1:
            parser.error("missing archive")
        else:
            from deploy import extract
            # get config file
            f = extract.get_project_config(args[0])
            config = parse_config(f)
            
            # FIXME: sanity checks

            #extract.extract_project(args[0])
            
