#! /usr/bin/env python
# -*- coding: utf-8
import sys
from datetime import datetime


#redirect error output to a file...
fsock = open('err_pyDelest.log','a')
sys.stderr = fsock

def stderrprint(text):
    print >> sys.stderr, str(datetime.now())[:-7]+ " " + text
    sys.stderr.flush()
    
