# -*- coding: utf-8
from datetime import datetime, timedelta
from string import ljust
import re

#This is my list of relevant labels that I want for the final display / DB
relevance_list = ['PAPP','PTEC','HCHP','HCHC','ADPS']
sql_list       = ['PAPP','PTEC','CPT','ADPS']

class Frame:
    """ This is the class representing a whole Frame. Everything between STX and ETX or EOT should go here."""
    def __init__(self):
        self.timestamp = datetime.now().replace(microsecond=0)
        self.infodict = {}

    def build(self, frame_string):
        m = frame_string.split('\n')
        for c in m:
            if len(c) > 3:
                info=Information(c)
                if info.valid and info.label in relevance_list :
                    self.infodict[info.label] = info
    
    def __repr__(self):
        out = ''
        for key in relevance_list:
            if key in self.infodict:
                out+=str(self.infodict[key].value)+" "
        return str(self.timestamp) + " " + out + '\n'

    def __eq__(self, other):
        for key in self.infodict.keys():
            if not ((other.infodict.has_key(key)) and (self.infodict[key] == other.infodict[key])):
                return False
        return True
    
    def age(self):
        return datetime.now().replace(microsecond=0) - self.timestamp

    def toSQL(self):
        sqlfix='INSERT INTO teleinfo VALUES '
        out= sqlfix + "('"+str(self.timestamp)+"'"
        for key in sql_list:
            if key in self.infodict:
                out+=",'"+self.infodict[key].value+"'"
            elif key == "CPT":
                if 'PTEC' in self.infodict:
                    if self.infodict['PTEC'].value == 'HC..':
                        if 'HCHC' in self.infodict:
                            out+=",'"+self.infodict['HCHC'].value+"'"
                        else:
                            out+=",''"
                    elif self.infodict['PTEC'].value == 'HP..':
                        if 'HCHP' in self.infodict:
                            out+=",'"+self.infodict['HCHP'].value+"'"
                        else:
                            out+=",''"
                else:
                    out+=",''"
            else:
                out+=",''"
        out+=");\n"
        return out


class Information:
    """ This is the base class for all Information fields that are coming.
It holds everything between the LF and the CR characters """
    info_regexp = re.compile("\A(?P<LABEL>\w{4,8})[ ](?P<VALUE>[\w.]{1,12})[ ](?P<CHECKSUM>.)")

    def __init__(self,data):
        self.label = ''
        self.value = ''
        self.checksum = ''
        self.valid = False
        self.build(data)
        self.check()

    def build(self, data):
        m = self.info_regexp.match(data)
        if m:
            self.label    = m.group('LABEL')
            self.value    = m.group('VALUE')
            self.checksum = m.group('CHECKSUM')
       
    def check(self):
        """ This is the method handling the checksum stuff """
        sum = 0
        a = self.label + ' ' + self.value
        for character in a:
            sum += ord(character)
        sum = (sum & 0x3f) + 0x20
        if chr(sum) == self.checksum:
            self.valid = True
        else:
            self.valid = False

    def __repr__(self):
        val=''
        if not self.valid:
            val = '!'
        return ljust(self.label,8) + ':' + ljust(self.value,12) + val + '\n'

    def __eq__(self, other):
        if (self.label == other.label) and (self.value == other.value):
            return True
        else:
            return False
