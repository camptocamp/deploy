#!/usr/bin/env python
# -*- mode: python; indent-tabs-mode: nil; tab-width: 4 -*-
# vim: set tabstop=4 shiftwidth=4 expandtab:

import os
import sys

if len(sys.argv) == 1:
  print "Usage: test.py [options]"
  print "\t--sync"
  print "\t--sayhello"
  print
  sys.exit()

if sys.argv[1] == "--sync":
  print "rsync directory"
  os.system("rsync -avz -e 'ssh -i /home/mbornoz/deploy_id_rsa' /home/mbornoz/puppet-apache/ mbornoz@mbornoz.int.lsn:/home/mbornoz/puppet-apache/")

if sys.argv[1] == "--sayhello":
  print "execute a remote command"
  os.system("ssh -i /home/mbornoz/deploy_id_rsa mbornoz@mbornoz.int.lsn /home/mbornoz/test.py --sayhello")
