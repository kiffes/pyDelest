#! /usr/bin/env python
# -*- coding: utf-8
from datetime import datetime, timedelta
import re
import serial
import threading
import Queue
import time
from optparse import OptionParser
import sys
#import post
import os
import os.path
from teleinfo import Frame
#redesign
from Relays  import relay, RelayThread
from helpers import *
from Input   import InputThread, test_source
from SQL     import SQLThread
from Console import ConsoleDispThread 



teleinfo_port=''
relay_port=''

parser=OptionParser()
parser.add_option('-t', '--teleinfo',action="store", type="string", dest="teleinfo_port", help = "Serial port where the teleinformation comes from.",default=None)
parser.add_option('-r', '--relays',action="store", type="string", dest="relay_port", help="Serial port where the relays are controlled.")
parser.add_option('--leds', '-l', action="store_true", default=False, dest="leds_enable", help="Enable measure leds output.")
parser.add_option('--boost1', action="store_true", default=False, dest="boost_afternoon", help="Boost in the afternoon.")
parser.add_option('--boost2', action="store_true", default=False, dest="boost_morning", help="Boost in the morning.")
(options,args)=parser.parse_args()
parser.destroy()

stderrprint("Hello, i have started.")

if (options.teleinfo_port):
    teleinfo_port = options.teleinfo_port
else:
    print "Missing option: --teleinfo"
    exit(1)
if (options.relay_port):
    relay_port = options.relay_port
else:
    print "Missing option: --relays"
    exit(1)



InputThread.the_source = test_source(teleinfo_port)
if (InputThread == None):
    print "Error the teleinfo port does not seem to deliver any info"
    exit(1)


class TheGlobals():
    def __init__(self):
        self.p_app = 0
        self.ptec = '??'
        self.last_frame_time = datetime.now()
        self.Frame_Q = Queue.Queue(10) #This is a FIFO queue with max size = 10
        self.options = options
        self.ser_relay = None

globs = TheGlobals()
globs.ser_relay = serial.Serial(relay_port, 9600)
relay.the_writer = globs.ser_relay
 

inputthread=InputThread(globs)
inputthread.start()

displaythread=ConsoleDispThread(globs)
displaythread.start()

sqlthread=SQLThread(globs)
sqlthread.start()

relaythread=RelayThread(globs)
relaythread.start()

try:
    while True: pass
except KeyboardInterrupt:
    print "\nStopped by Keyboard Interrupt"
finally:
    print "Now stopping all the threads"
    sqlthread.stop()
    displaythread.stop()
    relaythread.stop()
    inputthread.stop()
    
    print "Now joining"
    sqlthread.join()
    displaythread.join()
    relaythread.join()
    inputthread.join()
    
    globs.ser_relay.close()
    fsock.close()
    print "Have a nice day."
