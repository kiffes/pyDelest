# -*- coding: utf-8
from teleinfo import Frame

#This is my list of relevant labels that I want for the final display / DB
relevance_list = ['PAPP','PTEC','HCHP','HCHC','ADPS']
sql_list       = ['PAPP','PTEC','CPT','ADPS']

class Element:
    """ """
    def __init__(self, Frame):
        self.begin_timestamp = Frame.timestamp
        self.end_timestamp   = 0
        self.ptec  = Frame.infodict['PTEC']
        if self.ptec == 'HC..':
            self.Wh_begin = Frame.infodict['HCHC']
        else:
            self.Wh_begin = Frame.infodict['HCHP']

        self.max_peak  = Frame.infodict['PAPP']
        self.min_peak  = Frame.infodict['PAPP']
        self.ptec  = Frame.infodict['PTEC']

    def update(self,Frame):
        if Frame.infodict['PTEC'] == self.ptec:
            if Frame.infodict['PAPP'] > self.max_peak:
                self.max_peak = Frame.infodict['PAPP']
            if Frame.infodict['PAPP'] < self.min_peak:
                self.min_peak = Frame.infodict['PAPP'] 

            if self.ptec == 'HC..':
                self.Wh = Frame.infodict['HCHC'] -  self.Wh_begin
            else:
                self.Wh = Frame.infodict['HCHP'] -  self.Wh_begin
            self.end_timestamp = Frame.timestamp

    def __repr__(self):
        out = ''
        out = self.begin_timestamp + \ 
              " -> " +               \
              self.end_timestamp  +  \
              " " + self.min_peak + " " + self.max_peak + " " + \
              self.Wh
        return out

    
    def toSQL(self):
        pass


