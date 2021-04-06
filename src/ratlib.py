#!/usr/bin/python

import sys, os
__SERVERSRCDIR = os.path.join(os.path.dirname(__file__), '../server/src')
sys.path.append(__SERVERSRCDIR)
import config
from config import dq
import  dqpackage.libdaq.timeutils as tmu

if __name__ == "__main__":
    print 'This is a library. Use standalone scripts.'
    import sys
    sys.exit(1)
