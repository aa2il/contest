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
import datetime
from rig_io.ft_tables import *
from scoring import CONTEST_SCORING
from dx.spot_processing import Station, Spot, WWV, Comment, ChallengeData

############################################################################################
    
# Scoring class for ARRL VHF contest - Inherits the base contest scoring class
class ARRL_VHF_SCORING(CONTEST_SCORING):
 
    def __init__(self,P):
        CONTEST_SCORING.__init__(self,P.contest_name)

        self.MY_CALL = P.SETTINGS['MY_CALL']
        self.MY_GRID = P.SETTINGS['MY_GRID']

        self.BANDS = ['6m','2m','70cm']
        self.NQSOS = OrderedDict()
        grids = []
        for b in self.BANDS:
            grids.append((b,set([])))
            self.NQSOS[b]=0
        self.grids = OrderedDict(grids)
        self.nqsos=0

    # Scoring routine for ARRL VHF contest for a single qso
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE):
        #print('\nrec=',rec)

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
            sys.exit(0)
        self.grids[band].add(grid)

        # Check for valid grid
        valid = len(grid)==4 and grid[0:2].isalpha() and grid[2:4].isdigit()
        if not valid:
            print('\nVHF SCORING: Not a valid grid: call=',call,'\tgrid=',grid)
            sys.exit(0)

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
            sys.exit(0)

        self.nqsos+=1
        if not dupe:
            if band=='70cm':
                qso_points=2
            else:
                qso_points=1
            
            self.nqsos2 += 1;
            self.total_points += qso_points

            self.NQSOS[band] +=1

#                              --------info sent------- -------info rcvd--------
#QSO: freq  mo date       time call              grid   call              grid 
#QSO: ***** ** yyyy-mm-dd nnnn ***************** ****** ***************** ******
#QSO:   144 PH 2003-06-14 2027 NJ2L              FN12fr VE3FHU            FN25
#0000000001111111111222222222233333333334444444444555555555566666666667777777777
#1234567890123456789012345678901234567890123456789012345678901234567890123456789

        line='QSO: %5d %2s %10s %4s %-17s %-6s %-17s %-6s' % \
            (freq_mhz,mode,date_off,time_off, \
             self.MY_CALL,self.MY_GRID[:4],call,grid)

        #print(line)
        return line


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

        print('\nNo. QSOs      =',self.nqsos)
        print('No. Uniques   =',self.nqsos2)
        print('QSO points    =',self.total_points)
        print('Multipliers   =',mults)
        print('Claimed Score =',self.total_points*mults)
    
