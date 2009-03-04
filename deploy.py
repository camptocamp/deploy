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
    c_group.add_option("--symlink",
                       action="store_true", dest="symlink", default=True,
                       help="use symlinks for 'files' and 'code' [default]")

    c_group.add_option("--no-symlink",
                       action="store_false", dest="symlink",
                       help="don't use symlinks for 'files' and 'code' (copy content)")
    
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
            destdir = deploy.create.create_update_archive(join(args[0], config.get('DEFAULT', 'project')),
                                                          options.create)
            
            deploy.database.dump(dict(config.items('databases')),
                                 join(destdir, 'databases'))
            
            deploy.files.dump(dict(config.items('files')),
                              join(destdir, 'files'),
                              options.symlink)
            
            deploy.code.dump(dict(config.items('code')),
                             join(destdir, 'code'),
                             options.symlink)

            # if symlinks, use:: rsync -avz --copy-links bar ab-swisstopo.camptocamp.net:/tmp
    elif options.extract:
        config = deploy.config.parse_config(os.path.join(options.extract))
        srcdir = deploy.extract.get_archive_dir(options.extract)

        # FIXME: run prerestore.sh (apache and postgresql)

        deploy.database.restore(dict(config.items('databases')), 
                                join(srcdir, 'databases'))

        deploy.files.restore(dict(config.items('files')), 
                             join(srcdir, 'files'))
        
        deploy.code.restore(dict(config.items('code')),
                            join(srcdir, 'code'))


        # FIXME: run postrestore.sh (apache and postgresql)
