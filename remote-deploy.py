#!/usr/bin/env python
# -*- mode: python; indent-tabs-mode: nil; tab-width: 4 -*-
# vim: set tabstop=4 shiftwidth=4 expandtab:

import os
import commands

if __name__=="__main__": 
  sshcmd = os.getenv('SSH_ORIGINAL_COMMAND')

  os.system("echo %s > /tmp/ssh-original-command" % sshcmd)

  if sshcmd.startswith("rsync --server"):
    os.system(sshcmd)
  elif sshcmd.startswith("/home/mbornoz/test.py --sayhello"):
    a = commands.getoutput("hostname -f")
    print a
  else:
    print "rejected"
