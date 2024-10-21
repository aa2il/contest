############################################################################################
#
# mak.py - Rev 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring Makrothen RTTY contest
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

# Need this for Makrothen and WW-DIGI - it was broke but looking up error helped to fix it
from pyhamtools.locator import calculate_distance

#######################################################################################
    
# Scoring class for CQ WPX - Inherits the base contest scoring class
class MAKROTHEN_SCORING(CONTEST_SCORING):
 
    def __init__(self,contest):
        CONTEST_SCORING.__init__(self,contest,'MAKROTHEN-RTTY')
        print('Makrothen RTTY Scoring Init ...')
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.sec_cnt = np.zeros((len(self.BANDS)))
        self.calls=set([])

        # Determine start & end dates/times
        now = datetime.datetime.utcnow()
        year=now.year
        month=10

        day1=datetime.date(year,month,1).weekday()                  # Day of week of 1st of month - 0=Monday, 6=Sunday
        sat2=1 + ((5-day1) % 7) + 7                                # Day no. for 2nd Saturday = 1 since day1 is the 1st of the month
                                                                   #    no. days until 1st Saturday (day 5) + 7 more days 
        
        self.date0=datetime.datetime(year,month,sat2,0)            
        self.date1 = self.date0 + datetime.timedelta(hours=40)     
        
        if True:
            print('now=',now)
            print('day1=',day1,'\tsat2=',sat2)
            print('date0=',self.date0)
            print('date1=',self.date1)
            #sys.exit(0)

        # Name of output file
        self.output_file = self.MY_CALL+'_MAKROTHEN-RTTY_'+str(self.date0.year)+'.CBR'
        
    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_STATE)
        fp.write('ARRL-SECTION: %s\n' % self.MY_SECTION)
                            
    # Scoring routine for Makrothen RTTY contest
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE,HIST2):
        VERBOSITY=0
        if VERBOSITY>0:
            print('rec=',rec)
            sys.exit(0)

        # Check for correct contest
        if "contest_id" in rec:
            id   = rec["contest_id"].upper()
        else:
            id=''
        if id!='MAKROTHEN':
            if VERBOSITY>0:
                print('contest=',self.contest,id)
                print('QSO not part of MAKROTHEN contest - skipping')
            return
        
        # Pull out relavent entries
        call = rec["call"]
        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        band = rec["band"]
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%d-%m')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
        if "gridsquare" in rec:
            grid = rec["gridsquare"]
        else:
            grid = rec["qth"]
    
        # Compute score for this entry
        dx_km = int( calculate_distance(grid,self.MY_GRID[:4]) +0.5 )
        if dx_km > self.max_km:
            self.max_km=dx_km
            self.longest=rec
        if not dupe:
            self.nqsos2 += 1;

        if dupe:
            mult=0
        elif dx_km==0:
            dx_km=100
            mult=1
        elif band=='80m':
            mult=2
        elif band=='40m':
            mult=1.5
        else:
            mult=1
            
        self.total_km += dx_km
        self.total_score += mult*dx_km
    
        #print call,grid,dx_km
    
        line='QSO: %5d RY %10s %4s %-13s %-6s %-13s %-6s' % \
            (freq_khz,date_off,time_off,self.MY_CALL,self.MY_GRID[:4],call,grid[0:4].upper())

        return line

    # Summary & final tally
    def summary(self):

        avg_dx_km = self.total_km / self.nqsos2
        print(self.nqsos2,self.max_km,avg_dx_km,self.total_score)
        print('\nLongest DX:',self.max_km,'km')
        print(self.longest)
        print('\nAverage DX:',avg_dx_km,'km')
        
        print('\nnqsos         =',self.nqsos2)
        print('Claimed score =',self.total_score)
        
