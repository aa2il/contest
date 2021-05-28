############################################################################################
#
# cqww.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring CQ WW contests
#
############################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
############################################################################################

import sys
import datetime
from rig_io.ft_tables import *
from scoring import CONTEST_SCORING
from dx.spot_processing import Station, Spot, WWV, Comment, ChallengeData

############################################################################################
    
# Scoring class for CQ WW - Inherits the base contest scoring class
class CQ_WW_SCORING(CONTEST_SCORING):
 
    def __init__(self,contest):
        CONTEST_SCORING.__init__(self,contest)

        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        mults = []
        for b in self.BANDS:
            mults.append((b,set([])))
        self.mults = OrderedDict(mults)

        # Point to proper scoring function
        if contest=='CQ-WW-SSB' or contest=='CQ-WW-CW':
            self.qso_scoring = self.qso_scoring_cw
        elif contest=='CQ-WW-RTTY':
            self.qso_scoring = self.qso_scoring_rtty
        else:
            print('WTF?')
            
    # Scoring routine for CQ WW CW & SSB
    def qso_scoring_cw(self,rec,dupe,qsos,HIST,MY_MODE):
        #print ' '
        #print rec

        # Pull out relavent entries
        call = rec["call"]
        freq_khz = int( 1000*float(rec["freq"]) + 0.0 )
        band = rec["band"]
        if 'qth' in rec :
            qth = rec["qth"]
        else:
            qth = ''

        dx_station = Station(call)
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')

        # Minor corrections
        if qth=='':
            qth=dx_station.cqz
        try:
            zone=int(qth)
        except:
            print('Problem converting zone:',qth)
            print(rec)
            zone = int( dx_station.cqz )
            #sys.exit(0)

        warning=False
        problem=False
        
        if not dupe:
            self.nqsos2 += 1;
            if dx_station.country=='United States':
                qso_points=0
            elif dx_station.continent=='NA':
                qso_points=2
            else:
                qso_points=3
            self.total_points += qso_points

            self.mults[band].add(str(zone))
            self.mults[band].add(dx_station.country)

        if MY_MODE=='CW':
            mode='CW'
            rst_out=599
            rst_in=599
        elif MY_MODE=='SSB':
            mode='PH'
            rst_in=59
        else:
            mode='??'
            
#QSO:  3799 PH 2000-10-26 0711 AA1ZZZ          59  05     K9QZO         59  04     0
        line='QSO: %5d %2s %10s %4s %-13s %3d %2.2d %-13s %3d %2.2d  0' % \
            (freq_khz,mode,date_off,time_off,MY_CALL,rst_out,int(MY_CQ_ZONE),call,rst_in,zone)

        if warning or problem:
            print(' ')
            print(rec)

            print(dx_station)
            pprint(vars(dx_station))
            
            print('Call =',call)
            print('Freq =',freq_khz)
            print('Band =',band)
            print('Zone =',zone,dx_station.cqz)
            print('State=',state)
            print('Date =',date_off)
            print('Time =',time_off)
            
            print(line)
            if problem:
                sys,exit(0)

        return line
                        
    # Scoring routine for CQ WW RTTY
    def qso_scoring_rtty(self,rec,dupe,qsos,HIST,MY_MODE):
        #print ' '
        #print rec

        # Pull out relavent entries
        call = rec["call"]
        freq_khz = int( 1000*float(rec["freq"]) + 0.0 )
        band = rec["band"]
        if 'name' in rec :
            name = rec["name"]
        else:
            name = ''
        if 'qth' in rec :
            qth = rec["qth"]
        else:
            qth = ''

        # There was some inconsitencies in where things were stored
        if qth.isdigit() and not name.isdigit():
            zone  = int(qth)
            state = name.upper()
        elif not qth.isdigit() and name.isdigit():
            zone  = int(name)
            state = qth.upper()
        else:
            print('*** ERROR *** Cant resolve zone and state')
            problem=True

        dx_station = Station(call)
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')

        # Minor corrections
        if state=='' or zone==31:
            state='DX'

        warning=False
        problem=False
        
        if ((state in STATES) and zone!=CQ_ZONES[state] ) or \
           ( not (state in STATES) and zone!=dx_station.cqz):
            print('*** Zone Mismatch ***')
            warning=True;
            self.warnings += 1
            
        if zone>=3 and zone<=5 and not (state in CQ_STATES):
            # This is not quite right for some parts of Canada but go with it for now
            print('*** Expected US/Canada  ***')
            problem=True;
        elif (zone<3 or zone>5) and state!='DX':
            # This is not quite right for some parts of Canada but go with it for now
            print('*** Expected DX ***')
            problem=True;

        if not dupe:
            self.nqsos2 += 1;
            if dx_station.country=='United States':
                qso_points=1
            elif dx_station.continent=='NA':
                qso_points=2
            else:
                qso_points=3
            self.total_points += qso_points

            self.mults[band].add(str(zone))
            self.mults[band].add(dx_station.country)
            if state!='DX':
                self.mults[band].add(state)
                   
            
#QSO: 14073 RY 2008-09-27 0005 HC8N 599 10 DX WC2C   599 05 NY 
        line='QSO: %5d RY %10s %4s %-13s 599 %2.2d %-2s %-13s 599 %2.2d %-3s  0' % \
            (freq_khz,date_off,time_off,MY_CALL,int(MY_CQ_ZONE),MY_STATE,call,zone,state)

        if warning or problem:
            print(' ')
            print(rec)

            print(dx_station)
            pprint(vars(dx_station))
            
            print('Call =',call)
            print('Freq =',freq_khz)
            print('Band =',band)
            print('Zone =',zone,dx_station.cqz)
            print('State=',state)
            print('Date =',date_off)
            print('Time =',time_off)
            
            print(line)
            if problem:
                sys,exit(0)

        return line
                        
    # Summary & final tally
    def summary(self):

        print('nqsos2=',self.nqsos2)
        print('num warnings=',self.warnings)

        #print('MULTS:',self.mults)
        mults=0
        for b in self.BANDS:
            m = list( self.mults[b] )
            #print('m=',m)
            m.sort()
            #print('m=',m)
            print(' ')
            print(b,' Mults:',m)
            mults+=len(m)

        print('\nnqsos         =',self.nqsos2)
        print('qso points    =',self.total_points)
        print('mults         =',mults)
        print('Claimed score =',self.total_points*mults)
    
