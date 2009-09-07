#!/usr/bin/env python

from optparse import OptionParser, OptionGroup
import os, sys, socket, time
import logging
from logging.handlers import SysLogHandler
import deploy
from deploy.common import rmtree_silent, setup_hooks, run_hook, dirname

def setup_logging(verbose=False):
    # configure the root logger
    fqdn = socket.getfqdn()
    logging.getLogger('').setLevel(logging.DEBUG)

    format = "[%(name)s] %(message)s"
   
    syslog = SysLogHandler(address='/dev/log')
    syslog.setFormatter(logging.Formatter(format))
    logging.getLogger('').addHandler(syslog)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(fqdn + " " + format))
    if not verbose:
        console.setLevel(logging.ERROR)

    logging.getLogger('').addHandler(console)

components = ['databases', 'files', 'code']

if __name__ == '__main__':
    
    usage = "usage: %prog -c [OPTIONS]... CONFIG_FILE DIRECTORY\n" + \
            "   or: %prog -x [OPTIONS]... DIRECTORY\n" + \
            "   or: %prog -r [OPTIONS] CONFIG_FILE HOST"

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

    c_group.add_option("--tables",
                       default=None,
                       help="only include TABLES. eg: '--tables foo,bar.baz' to include the " +
                       "database 'foo' and the 'baz' table from the 'bar' database")

    c_group.add_option("--symlink",
                       action="store_true", dest="symlink",
                       help="use symlinks for 'files' and 'code'")

    c_group.add_option("--no-symlink",
                       action="store_false", dest="symlink", default=False,
                       help="don't use symlinks for 'files' and 'code' (copy content) [default]")
    
    x_group.add_option("-x", "--extract",
                       action="store_true",
                       help="extract files from an archive")

    x_group.add_option("-d", "--delete",
                       action="store_true", dest="delete" ,default=True,
                       help="delete the archive after the restoration [default]")

    x_group.add_option("-k", "--keep",
                       action="store_false", dest="delete",
                       help="don't delete the archive after the restoration")

    r_group.add_option("-r", "--remote",
                       action="store_true",
                       help="create, copy and restore an archive to a remote server")

    r_group.add_option("--no-time-dir",
                       action="store_false", dest="timedir", default=True,
                       help="don't create separated archive directory for each remote deploy [default false]")

    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=True,
                      help="make lots of noise [default]")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose",
                      help="be vewwy quiet")

    parser.add_option("-e", "--env",
                      default='',
                      help="additionals environement variables, eg: '-e target=prod,foo=bar'")

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
        
    if not options.create and not options.extract and not options.remote:
        parser.error("missing action")

    if options.components == 'all':
        options.components = components

    if options.tables and 'databases' not in options.components:
        parser.error("can't have a 'tables' option without the 'databases' components")
    
    if options.remote:
        config = deploy.config.parse_config(args[0], options.env)
        packages_dir = config.get('main', 'packages_dir')
        remote_destination = args[1:]

        if not remote_destination:
            parser.error("missing hosts or profile name")
        
        elif len(remote_destination) == 1:
            # find a remote profile
            if config.has_section('remote_hosts') and config.has_option('remote_hosts', remote_destination[0]):
                hosts = [h.strip() for h in config.get('remote_hosts', remote_destination[0]).split(',')]
            else:
                hosts = remote_destination
        else:
            # simple hosts list
            hosts = remote_destination

        logger.info("remote deploy to '%(remote)s'" %{'remote': hosts})

        destpath = config.get('DEFAULT', 'project')
        if options.timedir:
            destpath += '_' + str(int(time.time()))
        args[1] = os.path.join(packages_dir, destpath)

        # let's start creating the archive
        options.create = True
        
    if options.create:
        if len(args) < 2:
            parser.error("missing config and/or archive destination")
        else:
            config = deploy.config.parse_config(args[0], options.env)
            has_custom_hooks = setup_hooks(config, options.verbose)
            
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
                                     options.tables,
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
                for host in hosts:
                    if deploy.remote.remote_copy(dirname(destdir), host):
                        if deploy.remote.remote_extract(dirname(destdir), host, options):
                            #remote_extract success
                            pass
                        else:
                            #remote_extract failed:
                            logger.error("error while deploying to '%s'."%host)
                            sys.exit(1)
                    else:                
                         #remote_copy failed
                         logger.error("error while copying archive to '%s'."%host)
                         sys.exit(1)
            else:
                # no remote mode
                sys.exit(0)
            
    elif options.extract:
        if len(args) < 1:
            parser.error("missing archive path")
        else:
            srcdir = deploy.extract.get_archive_dir(args[0])
            config = deploy.config.parse_config(srcdir, options.env)
            logger.info("restoring archive from '%(archive)s'" %{'archive': srcdir})
            
            setup_hooks(config, options.verbose)
            
            run_hook('pre-restore')

            deploy.database.restore(dict(config.items('databases')), 
                                    os.path.join(srcdir, 'databases'))

            deploy.files.restore(dict(config.items('files')), 
                                 os.path.join(srcdir, 'files'))
        
            destdir = deploy.code.restore(dict(config.items('code')),
                                          os.path.join(srcdir, 'code'))
            if destdir:
                deploy.apache.restore(dict(config.items('apache')), destdir)

            run_hook('post-restore')

            if options.delete:
                logger.info("deleting '%(srcdir)s'"%{'srcdir': srcdir})
                rmtree_silent(srcdir)
                
            logger.info("done restoring")
            
            sys.exit(0)
