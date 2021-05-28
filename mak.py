############################################################################################
#
# mak.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
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
        CONTEST_SCORING.__init__(self,contest)
        print('FD Scoring Init')
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.sec_cnt = np.zeros((len(self.BANDS)))
        self.calls=set([])

    # Scoring routine for Makrothen RTTY contest
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE):

        # Pull out relavent entries
        call = rec["call"]
        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        band = rec["band"]
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%d-%m')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
        grid = rec["gridsquare"]
    
        # Compute score for this entry
        dx_km = int( calculate_distance(grid,MY_GRID[:4]) +0.5 )
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
            (freq_khz,date_off,time_off,MY_CALL,MY_GRID[:4],call,grid[0:4].upper())

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
        
