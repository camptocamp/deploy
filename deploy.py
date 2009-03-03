#!/usr/bin/env python

from optparse import OptionParser, OptionGroup
import logging, os
from os.path import join
import logging

import deploy

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    usage = "usage: %prog [OPTIONS...] [FILE]..."

    parser = OptionParser(usage)
    c_group = OptionGroup(parser, "Create an archive")
    x_group = OptionGroup(parser, "Extract an archive")

    c_group.add_option("-c", "--create",
                       action="store", dest="create",
                       metavar="config",
                       help="create a new archive")
    x_group.add_option("-x", "--extract",
                       action="store", dest="extract",
                       metavar="archive",
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

    parser.add_option_group(c_group)
    parser.add_option_group(x_group)

    (options, args) = parser.parse_args()

    if options.create and options.extract:
        parser.error("options -c and -x are mutually exclusive")
    if not options.create and not options.extract:
        parser.error("missing action")

    if options.create:
        if len(args) < 1:
            parser.error("missing destination")
        else:
            config = deploy.config.parse_config(options.create)
            # create 
            destdir = deploy.create.create_update_archive(join(args[0], config.get('DEFAULT', 'project')),
                                                          options.create)
            
            deploy.database.dump(dict(config.items('databases')), 
                                 join(destdir, 'databases'))

#             files.dump(dict(config.items('files')), 
#                        join(destdir, 'files'))
            
#             code.dump(dict(config.items('code')),
#                       join(destdir, 'code'))
            
    elif options.extract:
        config = deploy.config.parse_config(os.path.join(options.extract))
        srcdir = deploy.extract.get_archive_dir(options.extract)
        
        deploy.database.restore(dict(config.items('databases')), 
                                join(srcdir, 'databases'))


        # if not error: run preextract.sh (apache and postgresql)
        #extract.extract_project(args[0])

        # if not error: run postextract.sh (apache and postgresql)
