############################################################################################
#
# wwdigi.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring World Wide Digi contest.
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
from pyhamtools.locator import calculate_distance

############################################################################################
    
# Scoring class for WW DIGI contest - Inherits the base contest scoring class
class WWDIGI_SCORING(CONTEST_SCORING):
 
    def __init__(self,P):
        CONTEST_SCORING.__init__(self,'WW-DIGI',mode='DIGI')
        print('WW DIGI Scoring Init')

        self.MY_CALL = P.SETTINGS['MY_CALL']
        self.MY_GRID = P.SETTINGS['MY_GRID']
        #self.MY_STATE    = P.SETTINGS['MY_STATE']

        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.NQSOS = OrderedDict()
        grids = []
        for b in self.BANDS:
            grids.append((b,set([])))
            self.NQSOS[b]=0
        self.grid_fields = OrderedDict(grids)
        self.nqsos=0

        # Determine contest time - assumes this is dones wihtin a few hours of the contest
        now = datetime.datetime.utcnow()
        day=31
        start_hour=12
        self.date0=datetime.datetime(now.year,now.month,day,start_hour)
        self.date1 = self.date0 + datetime.timedelta(hours=12)
                
        
    # Scoring routine for ARRL VHF contest for a single qso
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE):
        #print('\nrec=',rec)

        # Pull out relavent entries
        call = rec["call"]
        freq_khz = int( 1000*float(rec["freq"]) + 0.5 )
        band = rec["band"]

        grid = rec["gridsquare"]
        field = grid[:2].upper()
        self.grid_fields[band].add(field)

        # Check for valid grid
        valid = len(grid)==4 and grid[0:2].isalpha() and grid[2:4].isdigit()
        if not valid:
            print('\nWW DIGI SCORING: Not a valid grid: call=',call,'\tgrid=',grid)
            sys.exit(0)

        #print('call=',call)
        
        dx_station = Station(call)
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')

        # Compute score for this entry
        dx_km = int( calculate_distance(grid,self.MY_GRID[:4]) +0.5 )
        qso_points = 1+int(dx_km/3000.)
        if dx_km > self.max_km:
            self.max_km=dx_km
            self.longest=rec
            
        self.nqsos+=1
        if not dupe:
            self.total_km += dx_km
            self.nqsos2 += 1;
            self.total_points += qso_points

            self.NQSOS[band] +=1

#                              ------info sent------- ------info rcvd-------
#QSO: freq  mo date       time call          exch     call          exch        t
#QSO: ***** ** yyyy-mm-dd nnnn ************* ******** ************* ********    n
#QSO:  3595 DG 2019-08-31 1711 HC8N          EI00     W1AW          FN32        0
#000000000111111111122222222223333333333444444444455555555556666666666777777777788
#123456789012345678901234567890123456789012345678901234567890123456789012345678901

        line='QSO: %5d DG %10s %4s %-13s %-8s %-13s %-8s     0' % \
            (freq_khz,date_off,time_off,self.MY_CALL,self.MY_GRID[:4],call,grid)

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
    
