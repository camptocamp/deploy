#!/usr/bin/env python

from optparse import OptionParser, OptionGroup
import os
import logging
from deploy.common import rmtree_silent, run_hook
logger = logging.getLogger('main')

import deploy

components = ['databases', 'files', 'code']
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    usage = "usage: %prog -c [OPTIONS]... FILE DIRECTORY\n" + \
            "   or: %prog -x [OPTIONS]... DIRECTORY"

    parser = OptionParser(usage)
    c_group = OptionGroup(parser, "Create an archive")
    x_group = OptionGroup(parser, "Extract an archive")

    c_group.add_option("-c", "--create",
                       action="store_true",
#                        metavar="config",
                       help="create a new archive")
    c_group.add_option("--components",
                       default="all",
                       help="restrict component to update. [%s]. default to all" % ','.join(components))

    c_group.add_option("--symlink",
                       action="store_true", dest="symlink", default=True,
                       help="use symlinks for 'files' and 'code' [default]")

    c_group.add_option("--no-symlink",
                       action="store_false", dest="symlink",
                       help="don't use symlinks for 'files' and 'code' (copy content)")
    
    x_group.add_option("-x", "--extract",
                       action="store_true",
#                        metavar="archive",
                       help="extract files from an archive")


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

    if options.components == 'all':
        options.components = components
        
    if not options.create and not options.extract:
        parser.error("missing action")

    if options.create:
        if len(args) < 2:
            parser.error("missing config and/or archive destination")
        else:
            config = deploy.config.parse_config(args[0])
            destdir = os.path.join(args[1], config.get('DEFAULT', 'project'))

            destpath = dict([(c, os.path.join(destdir, c)) for c in components])

            run_hook('pre-create')

            deploy.create.create_update_archive(destdir, args[0])

            if 'databases' in options.components:
                deploy.database.dump(dict(config.items('databases')),
                                     destpath['databases'])
            else:
                logger.debug("removing '%(path)s'" %{'path': destpath['databases']})
                rmtree_silent(destpath['databases'])
                
            if 'files' in options.components:
                deploy.files.dump(dict(config.items('files')),
                                  destpath['files'],
                                  options.symlink)
            else:
                logger.debug("removing '%(path)s'" %{'path': destpath['files']})
                rmtree_silent(destpath['files'])
                
            if 'code' in options.components:
                deploy.code.dump(dict(config.items('code')),
                                 destpath['code'],
                                 options.symlink)
            else:
                logger.debug("removing '%(path)s'" %{'path': destpath['code']})
                rmtree_silent(destpath['code'])

            run_hook('post-create')

            logger.info("done")

            # if symlinks, use:: rsync -avz --copy-links bar ab-swisstopo.camptocamp.net:/tmp
    elif options.extract:
        if len(args) < 1:
            parser.error("missing archive path")
        else:
            config = deploy.config.parse_config(os.path.join(args[0]))
            srcdir = deploy.extract.get_archive_dir(args[0])

            run_hook('pre-restore')

            deploy.database.restore(dict(config.items('databases')), 
                                    os.path.join(srcdir, 'databases'))

            deploy.files.restore(dict(config.items('files')), 
                                 os.path.join(srcdir, 'files'))
        
            deploy.code.restore(dict(config.items('code')),
                                os.path.join(srcdir, 'code'))

            run_hook('post-restore')
