# -*- coding: utf-8 -*-

import sys
import os

def demonize(pidfile, umask=0, forks=2):
    
    if not pidfile:
        sys.stderr.write("Demonize error: uncorrect pidfile path '%s'\n" % pidfile)
        sys.exit(1)
    
    pidfile_dir = os.path.dirname(pidfile)
    
    if not os.path.exists(pidfile_dir):
        sys.stderr.write("Demonize error: no such directory: %s\n" % pidfile_dir)
        sys.exit(1)
    
    if not os.access(pidfile_dir, os.W_OK):
        sys.stderr.write("Demonize error: no access to %s\n" % pidfile_dir)
        sys.exit(1)
    
    def _fork(fork_num):
        try:
            os.fork() and sys.exit(0)
        except OSError, ex:
            sys.stderr.write("Error: %s" % ex)
            sys.exit(1)
        else:
            fork_num == 0 and ( os.setsid() or os.umask(umask) )

    map(_fork, xrange(forks))
    si = file("/dev/null", 'r')
    os.dup2(si.fileno(), sys.stdin.fileno())
    file(pidfile,'w+').write("%s" % os.getpid())
    return True


if __name__ == '__main__':
    
    demonize('./my.pid')
