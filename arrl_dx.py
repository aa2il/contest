############################################################################################
#
# arrl_dx.py - Rev 1.0
# Copyright (C) 2021-3 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring ARRL Internation DX contests.
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
from pprint import pprint
from utilities import reverse_cut_numbers

############################################################################################

TRAP_ERRORS = False
#TRAP_ERRORS = True

############################################################################################
    
# Scoring class for CQ WW - Inherits the base contest scoring class
class ARRL_INTL_DX_SCORING(CONTEST_SCORING):
 
    def __init__(self,P,MODE):
        CONTEST_SCORING.__init__(self,P,'ARRL-DX-'+MODE,MODE)
        print('ARRL Internation DX Scoring Init')

        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        dxccs  = []
        self.NQSOS = OrderedDict()
        self.POINTS = OrderedDict()
        for b in self.BANDS:
            dxccs.append((b,set([])))
            self.NQSOS[b]=0
            self.POINTS[b]=0
        self.dxccs = OrderedDict(dxccs)

        # Determine start & end dates/times - occurs on third full weekend in Feb,
        month=2
        now = datetime.datetime.utcnow()
        year=now.year

        day1=datetime.date(year,month,1).weekday()                         # Day of week of 1st of month - 0=Monday, 6=Sunday
        sat2=1 + ((5-day1) % 7) + 14                                   # Day no. for 3rd Saturday = 1 since day1 is the 1st of the month
                                                                       #    no. days until 1st Saturday (day 5) + 7 more days 
        
        self.date0=datetime.datetime(year,month,sat2,0) 
        self.date1 = self.date0 + datetime.timedelta(hours=48)         # ... and ends at 000 UTC on Monday
        
        # Manual override
        if False:
            self.date0 = datetime.datetime.strptime( "20190928 0000" , "%Y%m%d %H%M")  # Start of contest
            self.date0 = datetime.datetime.strptime( "20201128 0000" , "%Y%m%d %H%M")  # Start of contest
            self.date1 = self.date0 + datetime.timedelta(hours=48)
            
        if False:
            print('now=',now)
            print('day1=',day1,'\tsat2=',sat2)
            print('date0=',self.date0)
            print('date1=',self.date1)
            sys.exit(0)

        # Name of output file
        self.output_file = self.MY_CALL+'_ARRL-INTL-DX-'+MODE+'_'+str(self.date0.year)+'.LOG'
        
            
    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_STATE)
        fp.write('ARRL-SECTION: %s\n' % self.MY_SEC)
        fp.write('GRID-LOCATOR: %s\n' % self.MY_GRID)

    # Scoring routine for ARRL Internation DX CW & SSB
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE,HIST2):
        #print ' '
        #print rec

        # Pull out relavent entries
        call = rec["call"]
        freq_khz = int( 1000*float(rec["freq"]) + 0.0 )
        band = rec["band"]
        #if 'qth' in rec :
        qth = rec["qth"]
        #else:
        #    qth = ''
        
        dx_station = Station(call)
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')

        pwr=reverse_cut_numbers(qth)
        if pwr in ['KW','K','1K']:
            pwr='1000'
        elif pwr=='599':
            print('WOOOOOPS!',pwr)
            sys.exit(0)
        pwr=int(pwr)
        
        warning=False
        problem=False

        # Error checking
        
        if not dupe:
            self.nqsos2 += 1;
            self.NQSOS[band]+=1
            if dx_station.country in ['United States','Canada']:
                qso_points=0
            else:
                qso_points=3
            self.total_points += qso_points
            self.POINTS[band] += qso_points
            self.dxccs[band].add(dx_station.country)
            
        if MY_MODE=='CW':
            mode='CW'
            rst_out=599
            rst_in=599
        elif MY_MODE=='SSB':
            mode='PH'
            rst_in=59
        else:
            print('Unknown my Mode',MY_MODE)
            sys.exit(0)

        # Info for multi-qsos
        exch_in=str(rst_in)+' '+str(qth)
        if call in self.EXCHANGES.keys():
            self.EXCHANGES[call].append(exch_in)
        else:
            self.EXCHANGES[call]=[exch_in]
            
#QSO:  3799 PH 2000-10-26 0711 AA1ZZZ          59  05     K9QZO         59  04     0
        line='QSO: %5d %2s %10s %4s %-13s %3d %2s %-13s %3d %4s' % \
            (freq_khz,mode,date_off,time_off,self.MY_CALL,rst_out,self.MY_STATE,call,rst_in,pwr)

        if warning or problem:
            print(' ')
            print(rec)

            print(dx_station)
            pprint(vars(dx_station))
            
            print('Call =',call)
            print('Freq =',freq_khz)
            print('Band =',band)
            print('Date =',date_off)
            print('Time =',time_off)
            
            print(line)
            if problem and TRAP_ERRORS:
                sys,exit(0)

        return line
                        
    # Summary & final tally
    def summary(self):

        print('nqsos2=',self.nqsos2)
        print('num warnings=',self.warnings)

        #print('MULTS:',self.mults)
        ndxccs=0
        nqsos3=0
        dxccs=[]
        for b in self.BANDS:
            print('\n',b,'# QSOs=',self.NQSOS[b])
            nqsos3+=self.NQSOS[b]
            
            d = list( self.dxccs[b] )
            d.sort()
            print(b,' DXCCs :',d,len(d))
            ndxccs+=len(d)
            dxccs+=d

        print('\nBand\tQSOs\tPoints\tDXCCs')
        for b in self.BANDS:
            print(b,'\t',self.NQSOS[b],'\t',self.POINTS[b],'\t',len( self.dxccs[b] ))
        print('\nTotals:\t',nqsos3,'\t',self.total_points,'\t',ndxccs)

        print('\nClaimed score =',self.total_points*ndxccs)

        dxccs=list(set(dxccs)) 
        dxccs.sort()
        print('\nNo. unique DXCCs =',len(dxccs))
        print(dxccs)

