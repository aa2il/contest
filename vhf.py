############################################################################################
#
# vhf.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring ARRL VHF contest.
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
import os
import datetime
from rig_io.ft_tables import *
from scoring import CONTEST_SCORING
from dx.spot_processing import Station, Spot, WWV, Comment, ChallengeData

############################################################################################
    
TRAP_ERRORS = False
TRAP_ERRORS = True

############################################################################################
    
# Scoring class for ARRL VHF contest - Inherits the base contest scoring class
class ARRL_VHF_SCORING(CONTEST_SCORING):

    def __init__(self,P):

        # Determine contest based on month
        now = datetime.datetime.utcnow()
        month = now.strftime('%b').upper()
        print('month=',month)

        # Init base class
        CONTEST_SCORING.__init__(self,P,'ARRL-VHF-'+month,mode='MIXED')

        # Init special items for this class
        self.MY_CALL = P.SETTINGS['MY_CALL']
        self.MY_GRID = P.SETTINGS['MY_GRID']
        self.MY_SEC  = P.SETTINGS['MY_SEC']

        self.BANDS = ['6m','2m','70cm']
        self.NQSOS = OrderedDict()
        grids = []
        for b in self.BANDS:
            grids.append((b,set([])))
            self.NQSOS[b]=0
        self.grids = OrderedDict(grids)
        self.nqsos=0
        self.category_band='VHF-3-BAND'

        self.MODES=['CW','DG','PH']
        self.Nmode = OrderedDict()
        for m in self.MODES:
            self.Nmode[m]=0

        # History file
        self.history = os.path.expanduser( '~/Python/history/data/master.csv' )
        
        # Contest occurs on 2nd full weekend of June and Sept. For Jan, either 3rd or 4th
        day1=datetime.date(now.year,now.month,1).weekday()             # Day of week of 1st of month 0=Monday, 6=Sunday
        sat2=1 + ((5-day1) % 7) + 7                                    # Day no. for 2nd Saturday = 1 since day1 is the 1st of the month
                                                                       #    no. days until 1st Saturday (day 5) + 7 more days 
        if month=='JAN':
            sat2+=7                                                    # 3rd Saturday
            start=19                                                   # Jan starts at 1900 UTC on Saturday ...
        else:
            start=18                                                   # June & Sept start at 1800 UTC on Saturday ...
        self.date0=datetime.datetime(now.year,now.month,sat2,start) 
        self.date1 = self.date0 + datetime.timedelta(hours=33)         # ... and ends at 0300/0400 UTC on Monday
        print('day1=',day1,'\tsat2=',sat2,'\tdate0=',self.date0)
        #sys.exit(0)

        # Manual override
        if False:
            self.date0 = datetime.datetime.strptime( "20210612 1800" , "%Y%m%d %H%M")  # Start of contest
            self.date0 = datetime.datetime.strptime( "20210911 1800" , "%Y%m%d %H%M")  # Start of contest
            self.date1 = date0 + datetime.timedelta(hours=33)
      
        # Name of output file
        self.output_file = self.MY_CALL+'_'+month+'_VHF_'+str(self.date0.year)+'.LOG'
        
    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_SEC)
        fp.write('ARRL-SECTION: %s\n' % self.MY_SEC)
                    
    # Scoring routine for ARRL VHF contest for a single qso
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE,HIST2):
        keys=list(HIST.keys())
        if False:
            #print('\nrec=',rec)
            #print('\nqsos=',qsos)
            print('\nHIST=',HIST)
            sys,exit(0)

        # Pull out relavent entries
        call = rec["call"]
        band = rec["band"]
        if band=='6m':
            freq_mhz=50
        elif band=='2m':
            freq_mhz=144
        elif band=='70cm':
            freq_mhz=432
        #freq_mhz = int( float(rec["freq"]) )

        if 'gridsquare' in rec:
            grid = rec["gridsquare"].upper()
        elif 'srx_string' in rec:
            grid = rec["srx_string"].upper()
        else:
            print('\nUnable to determine grid',rec)
            if TRAP_ERRORS:
                sys.exit(0)

        if ',' in grid:
            a=grid.split(',')
            grid=a[0]
            print(call,a,grid)

        # Check for valid grid
        valid = len(grid)==4 and grid[0:2].isalpha() and grid[2:4].isdigit()
        if not valid:
            print('\nVHF SCORING: Not a valid grid: call=',call,'\tgrid=',grid)
            if TRAP_ERRORS:
                sys.exit(0)

        # Add to list of grids for each band
        if valid:
            self.grids[band].add(grid)
        
        #print('call=',call)
        
        dx_station = Station(call)
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')

        if rec["mode"]=='FT8':
            mode='DG'
        elif rec["mode"]=='CW':
            mode='CW'
        elif rec["mode"]=='FM' or  rec["mode"]=='USB':
            mode='PH'
        else:
            print('Unknown mode:',rec["mode"])
            if TRAP_ERRORS:
                sys.exit(0)

        self.nqsos+=1
        if not dupe:
            if band=='70cm':
                qso_points=2
            else:
                qso_points=1
            
            self.nqsos2 += 1;
            self.total_points += qso_points

            self.NQSOS[band] += 1
            self.Nmode[mode] += 1

#                              --------info sent------- -------info rcvd--------
#QSO: freq  mo date       time call              grid   call              grid 
#QSO: ***** ** yyyy-mm-dd nnnn ***************** ****** ***************** ******
#QSO:   144 PH 2003-06-14 2027 NJ2L              FN12fr VE3FHU            FN25
#0000000001111111111222222222233333333334444444444555555555566666666667777777777
#1234567890123456789012345678901234567890123456789012345678901234567890123456789

        line='QSO: %5d %2s %10s %4s %-17s %-6s %-17s %-6s' % \
            (freq_mhz,mode,date_off,time_off, \
             self.MY_CALL,self.MY_GRID[:4],call,grid)

        # Check against history
        # Assume WSJT decode was correct and only show cw/phone qsos
        if call in keys:
            grid2=HIST[call]['grid']
            if grid!=grid2 and rec["mode"]!='FT8':
                print('\n$$$$$$$$$$ Difference from history $$$$$$$$$$$')
                print(call,':  Current:',grid,' - History:',grid2)
                self.list_all_qsos(call,qsos)
                print(' ')

        else:
            if rec["mode"]!='FT8':
                print('\n++++++++++++ Warning - no history for call:',call)
                self.list_all_qsos(call,qsos)
        
        #print(line)
        return line


    # Routine to sift through station we had multiple contacts with to identify any discrepancies
    def check_multis(self,qsos):

        print('There were multiple qsos with the following stations:')
        qsos2=qsos.copy()
        qsos2.sort(key=lambda x: x['call'])
        calls=[]
        for rec in qsos2:
            calls.append(rec['call'])
        #print(calls)
        uniques = list(set(calls))
        uniques.sort()
        #print(uniques)

        for call in uniques:
            #print(call,calls.count(call))
            if calls.count(call)>1:
                for rec in qsos:
                    if rec['call']==call:
                        mode = rec["mode"]
                        band = rec["band"]
                        if 'qth' in rec:
                            qth  = rec["qth"].upper()
                        else:
                            qth  = rec["gridsquare"].upper()
                        print(call,'\t',band,'\t',mode,'\t',qth)
                print(' ')
                        

    # Summary & final tally
    def summary(self):
        
        print('GRIDS:',self.grids)
        mults=0
        for b in self.BANDS:
            grids = list( self.grids[b] )
            grids.sort()
            print('\n',b,'Grids:',grids)
            print(' No. QSOs,Mults:',self.NQSOS[b],len(grids))
            mults+=len(grids)

        print('\nBy Mode:')
        for m in self.MODES:
            print('\t',m,':\t',self.Nmode[m])
        print('\nNo. QSOs      =',self.nqsos)
        print('No. Uniques   =',self.nqsos2)
        print('QSO points    =',self.total_points)
        print('Multipliers   =',mults)
        print('Claimed Score =',self.total_points*mults)
    


    # Function to list all qsos with a particular call
    def list_all_qsos(self,call2,qsos):
        print('All QSOs with ',call2,':')
        same=True
        qth_old = None
        for rec in qsos:
            call = rec["call"].upper()
            if call==call2:
                print(rec)
                if 'qth' in rec:
                    qth  = rec["qth"].upper()
                else:
                    qth  = rec["gridsquare"].upper()
                band = rec["band"]
                print('call=',call,'\tqth=',qth,'\tband=',band)

                if qth_old:
                    same = same and (qth==qth_old)
                qth_old = qth

        if not same:
            print('&*&*&*&*&*&*&*& QTH MISMATCH *&*&*&*&*&*&*&&*&')
            print(call,'/R' in call2)
            if '/R' in call2:
                print('??? Move over ROVER ???')
            elif TRAP_ERRORS:
                sys.exit(0)

        
