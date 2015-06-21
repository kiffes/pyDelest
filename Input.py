#! /usr/bin/env python
# -*- coding: utf-8

from datetime import timedelta
import threading
import time
import serial
from teleinfo import Frame
#redesign
from Relays import relay, RelayThread
from helpers import *

# some special characters...
STX='\x02'
ETX='\x03'
EOT='\x04'

    
def test_source(port):
    source = serial.Serial(port,
                       baudrate=1200,
                       bytesize=7,
                       parity='N',
                       stopbits=1,
                       timeout=4,
                       xonxoff=0,
                       rtscts=0)
    initial = source.inWaiting()
    time.sleep(0.1)
    detected = source.inWaiting()-initial
    #print "Detected : ", detected, "on ", source.portstr
    if (detected > 5):
        return source
    else:
        source.close()
        return None


class InputThread (threading.Thread):
    """ This is the input thread """
    the_source = None

    def __init__(self, globinstance):
        threading.Thread.__init__(self)
        self.termevent=threading.Event()
        self.globs = globinstance

    def run(self):
        # This takes care of :
        # reading in the data from the teleinfo source,
        # creating frame objects stored in a queue => this is for database output
        # update application "global" variables

        started = False
        f_previous=Frame()
        while not self.termevent.isSet():
            if self.__class__.the_source != None:
                c = self.__class__.the_source.read(1)
                if (c == STX):
                    frame_string = '' # start a new frame string
                    f = Frame()       # needed to catch the start time.
                    started = True
                elif ((c == EOT or c == ETX) and started):
                    f.build(frame_string)
                    frame_string = ''
                    if not (f == f_previous):
                        self.globs.Frame_Q.put(f)
                        f_previous=f
                        self.globs.last_frame_time = f.timestamp          
                        if f.infodict.has_key('PAPP'):
                            self.globs.p_app = int(f.infodict['PAPP'].value)
                        if f.infodict.has_key('PTEC'):
                            self.globs.ptec  = f.infodict['PTEC'].value.rstrip('.')  #ptec is a string "HC" or "HP"
                elif ((len(c)>0) and started):
                    frame_string += c
                elif c == '':
                    # here it already means that the first timeout has elapsed...
                    if f_previous.age() > timedelta(0,80,0):
                        stderrprint("the source seems to be dry... closing it.")
                        self.__class__.the_source.close()
                        self.__class__.the_source = None
                        self.globs.ptec = '??'
            else:
                time.sleep (5)
                try:
                    self.__class__.the_source = test_source(self.globs.options.teleinfo_port)
                except:
                    pass
                else:
                    if self.__class__.the_source != None:
                        stderrprint("source, Welcome back !")
                
    def stop(self):
        self.termevent.set()
        if self.__class__.the_source != None:
            self.__class__.the_source.close()
            self.__class__.the_source = None
    
