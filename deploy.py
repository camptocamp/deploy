#!/usr/bin/env python

from optparse import OptionParser, OptionGroup
import os, sys, socket, time
import logging
from logging.handlers import SysLogHandler
import deploy
from deploy.common import rmtree_silent, set_hookdir, run_hook, dirname


def setup_logging(verbose=False):
    # configure the root logger
    fqdn = socket.getfqdn()
    logging.getLogger('').setLevel(logging.DEBUG)
   
    syslog = SysLogHandler(address='/dev/log')
    syslog.setFormatter(logging.Formatter("%(name)s: %(message)s"))
    logging.getLogger('').addHandler(syslog)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(fqdn + " %(name)s: %(message)s"))
    if not verbose:
        console.setLevel(logging.ERROR)

    logging.getLogger('').addHandler(console)

components = ['databases', 'files', 'code']

if __name__ == '__main__':
    
    usage = "usage: %prog -c [OPTIONS]... CONFIG_FILE DIRECTORY\n" + \
            "   or: %prog -x [OPTIONS]... DIRECTORY" + \
            "   or: %prog -r [OPTIONS] CONFIG_FILE DIRECTORY"

    parser = OptionParser(usage)
    c_group = OptionGroup(parser, "Create an archive")
    x_group = OptionGroup(parser, "Extract an archive")
    r_group = OptionGroup(parser, "Create, copy and extract")

    c_group.add_option("-c", "--create",
                       action="store_true",
                       help="create a new archive")
    c_group.add_option("--components",
                       default="all",
                       help="restrict component to update. [%s]. default to all" % ','.join(components))

    c_group.add_option("--symlink",
                       action="store_true", dest="symlink",
                       help="use symlinks for 'files' and 'code'")

    c_group.add_option("--no-symlink",
                       action="store_false", dest="symlink", default=False,
                       help="don't use symlinks for 'files' and 'code' (copy content) [default]")
    
    x_group.add_option("-x", "--extract",
                       action="store_true",
                       help="extract files from an archive")

    r_group.add_option("-r", "--remote",
                       action="store_true",
                       help="create, copy and restore an archive to a remote server")

    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=True,
                      help="make lots of noise [default]")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose",
                      help="be vewwy quiet")

    parser.add_option_group(c_group)
    parser.add_option_group(x_group)
    parser.add_option_group(r_group)

    # handle remote call: only allow rsync and extract
    sshcmd = os.getenv('SSH_ORIGINAL_COMMAND')

    if sshcmd is None:        
        # local mode
        (options, args) = parser.parse_args()
    else:
        if sshcmd.startswith("rsync --server"):
            os.system(sshcmd)
            sys.exit(0)
        elif sshcmd.startswith("deploy"):
            (options, args) = parser.parse_args(sshcmd.split()[1:])
        else:
            # FIXME: remote command error
            pass
        
    setup_logging(options.verbose)
    # get the main logger
    logger = logging.getLogger('deploy.main')

    if options.create and options.extract:
        parser.error("options -c and -x are mutually exclusive")

    if options.components == 'all':
        options.components = components
        
    if not options.create and not options.extract and not options.remote:
        parser.error("missing action")

    if options.remote:
        # FIXME: use config variable
        packages_dir = '/var/sig/deploy-archives/'
        
        config = deploy.config.parse_config(args[0])
        #remote_destination = args[1] + ':' + packages_dir
        remote_destination = args[1]
        logger.info("remote deploy to '%(remote)s'" %{'remote': remote_destination})
        args[1] = os.path.join(packages_dir,
                               config.get('DEFAULT', 'project') + '_' + str(int(time.time())))

        # let's start creating the archive
        options.create = True
        
    if options.create:
        if len(args) < 2:
            parser.error("missing config and/or archive destination")
        else:
            config = deploy.config.parse_config(args[0])
            has_custom_hooks = set_hookdir(config.get('main', 'hookdir'))
            
            destdir = os.path.join(args[1], config.get('DEFAULT', 'project'))

            destpath = dict([(c, os.path.join(destdir, c)) for c in components])

            run_hook('pre-create')

            deploy.create.create_update_archive(destdir, args[0])
            if has_custom_hooks:
                deploy.create.copy_hooks(config.get('main', 'hookdir'), destdir)
            else:
                # remove hook dir ?
                pass

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

            logger.info("done creating archive")
            if options.remote:
                if deploy.remote.remote_copy(dirname(destdir), remote_destination):
                    if deploy.remote.remote_extract(dirname(destdir), remote_destination):
                        #remote_extract success
                        pass
                    else:
                        #remote_extract failed:
                        # rename
                        pass
                else:
                     #remote_copy failed
                     # rename
                     pass
            else:
                sys.exit(0)
            
    elif options.extract:
        if len(args) < 1:
            parser.error("missing archive path")
        else:
            srcdir = deploy.extract.get_archive_dir(args[0])
            logger.info("restoring archive from '%(archive)s'" %{'archive': srcdir})
            
            config = deploy.config.parse_config(os.path.join(args[0]))
            set_hookdir(config.get('main', 'hookdir'))

            run_hook('pre-restore')

            deploy.database.restore(dict(config.items('databases')), 
                                    os.path.join(srcdir, 'databases'))

            deploy.files.restore(dict(config.items('files')), 
                                 os.path.join(srcdir, 'files'))
        
            destdir = deploy.code.restore(dict(config.items('code')),
                                          os.path.join(srcdir, 'code'))

            deploy.apache.restore(dict(config.items('apache')), destdir)

            run_hook('post-restore')

            logger.info("done restoring")
            sys.exit(0)
