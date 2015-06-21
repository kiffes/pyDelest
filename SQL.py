#! /usr/bin/env python
# -*- coding: utf-8

from datetime import datetime, timedelta
import re
import threading
import Queue
import sys
import os
import os.path
from teleinfo import Frame
#redesign
from Relays import relay, RelayThread


class SQLThread (threading.Thread):
    """ This thread handles the output stream for SQL stuff  """

    resp_regexp = re.compile("Uploaded: (?P<filename>\d\d\d\d-\d\d-\d\d_\d\d:\d\d\.txt) Size: (?P<size>[0-9.]*) .b (?P<ok_entries>\d*) / (?P<total_entries>\d*).*")
    max_entries = 35000

    def __init__(self, the_globs):
        threading.Thread.__init__(self)
        self.termevent=threading.Event()
        self.sqlfile = None
        self.new_file()
        self.globs = the_globs

    def run(self):
        while not self.termevent.isSet():
            try:
                f = self.globs.Frame_Q.get(True,3)  #this blocks 3s at most.
            except Queue.Empty:
                pass
            else:
                sqlreq = f.toSQL()
                self.the_count += 1
                self.sqlfile.write(sqlreq)
            
            if self.the_count >= self.max_entries:
                self.new_file()

    def new_file(self):
        if self.sqlfile != None:
            self.sqlfile.flush()
            old_name = self.sqlfile.name
            self.sqlfile.close()
            self.sqlfile = open(old_name,'r')
            self.sqlfile.seek(0)
            exception_info=""
            ok = False

            try:
                pass
            except:
                ok = False
                exception_info = str(sys.exc_info()[0])
                resp=(0,0,"An exception has occurred while uploading " + self.sqlfile.name)
           
            self.sqlfile.close()
            if ok:
                m = self.resp_regexp.match(resp[2])
                if m:
                    nb_ok = int(m.group('ok_entries'))
                    filename = m.group('filename')
                    if ((nb_ok >= (self.max_entries -2)) and (os.path.basename(self.sqlfile.name) == filename)):
                        os.unlink(self.sqlfile.name)
  
        d = datetime.now()
        filename='/home/cedric/'+str(d.date())+"_"+"%02i"%d.hour+":"+"%02i"%d.minute+'.txt'
        self.sqlfile=open(filename,'w')
        self.the_count=0

    def stop(self):
        self.termevent.set()
        self.sqlfile.close()
