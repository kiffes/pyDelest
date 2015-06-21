#! /usr/bin/env python
# -*- coding: utf-8

from datetime import datetime
import serial
import threading
import time
import sys
from teleinfo import Frame
from helpers import stderrprint

   
class RelayThread (threading.Thread):
    """ Relay control thread """
    def __init__(self, the_globs):
        threading.Thread.__init__(self)
        self.globs = the_globs
        self.termevent=threading.Event()
        self.chauffe_eau=relay(8)
        self.boost=relay(7)
        #self.delest_salon=relay(6)
        self.testrelays=[relay(1),relay(2),relay(3),relay(4),relay(5)]

    def run(self):
        
        while not self.termevent.isSet():
            ptec = self.globs.ptec
            p_app = self.globs.p_app
            options = self.globs.options
            if relay.the_writer == None:
                # lost the_writer...
                if self.globs.ser_relay.isOpen():
                    stderrprint("closing ser_relay")
                    self.globs.ser_relay.close()
                
                time.sleep(5)
                
                try:
                    self.globs.ser_relay = serial.Serial(options.relay_port, 9600)
                except:
                    pass
                else:
                    stderrprint("Relays, Welcome back !")
                    relay.the_writer = self.globs.ser_relay
            else:
                if options.leds_enable:
                    self.split(p_app)

                dt = datetime.now()  
                if (ptec == 'HC'):
                    self.chauffe_eau.On()
                else:
                    self.chauffe_eau.Off()

                boosting = False 
                if (options.boost_afternoon and (ptec == 'HC' and (dt.hour == 16 and dt.minute <= 30))) or \
                   (options.boost_morning   and (ptec == 'HC' and (dt.hour == 7  and dt.minute >= 30))):
                    self.boost.On()
                else:
                    self.boost.Off()
                time.sleep(2)
            
    def split(self, value):
        value = value / 200
        leds=5
        rolling=0
        while rolling < leds:
            digit = value % 2
            value = value / 2
            if (digit == 1):
                self.testrelays[rolling].On()
            else:
                self.testrelays[rolling].Off()
            rolling += 1

    def stop(self):
        self.termevent.set()
        self.chauffe_eau.Off()
        self.boost.Off()
        for relay in self.testrelays:
            relay.Off()

class relay:
    the_writer = None

    def __init__(self, idx):
        self.index = idx
        self.state = 0

    def Write(self,value):
        if self.__class__.the_writer != None:
            try:
                self.__class__.the_writer.write('\xFF'+chr(self.index)+value)
#            except OSError:
#                print "This is the OSError exception."
            except:
                stderrprint("This is an exception:" + str(sys.exc_info()[0]))
                stderrprint("Throwing away the_writer")
                self.__class__.the_writer = None
            else:
                if value=='\x01':
                    self.state=1 
                else:
                    self.state=0

    def On(self):
        self.Write('\x01')

    def Off(self):
        self.Write('\x00')

    def IsOn(self):
        return (self.state == 1)

    def IsOff(self):
        return (self.state == 0)

    def Toggle(self):
        if self.IsOn():
            self.Off()
        else:
            self.On()
        