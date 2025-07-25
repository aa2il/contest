############################################################################################
#
# wwdigi.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
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
        CONTEST_SCORING.__init__(self,P,'WW-DIGI',mode='DIGI')
        print('WW DIGI Scoring Init')

        self.MY_CALL = P.SETTINGS['MY_CALL']
        self.MY_GRID = P.SETTINGS['MY_GRID']

        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.band_cnt = np.zeros((len(self.BANDS)),dtype=int)
        self.NQSOS = OrderedDict()
        self.dxccs  = []
        grids = []
        for b in self.BANDS:
            grids.append((b,set([])))
            self.NQSOS[b]=0
        self.grid_fields = OrderedDict(grids)
        self.nqsos=0

        self.Qs=[]

        # Determine contest time - last weekend in August
        now = datetime.datetime.utcnow()
        year=now.year
        #year=2019                                                      # Override for testing
        day1=datetime.date(year,8,1).weekday()                          # Day of week of 1st of month 0=Monday, 6=Sunday
        sat1=1 + ((5-day1) % 7)                                         # Day no. for 1st Saturday
        sat2=sat1 + 3*7                                                 # Last Saturday of month
        if sat2+7<=31:
            sat2+=7
        
        start_hour=12
        self.date0=datetime.datetime(year,8,sat2,start_hour)
        self.date1 = self.date0 + datetime.timedelta(hours=24)

        if False:
            # Manual override
            self.date0 = datetime.datetime.strptime( "20190831 1200" , "%Y%m%d %H%M")  # Start of contest
            self.date1 = self.date0 + datetime.timedelta(hours=24)
        
        # Playing with dates
        if False:
            print('now=',now)
            print('day1=',day1)
            print(self.date0)
            print(self.date1)
            sys.exit(0)
            
        # Name of output file
        self.output_file = self.MY_CALL+'_WWDIGI_'+str(self.date0.year)+'.LOG'
        
    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_SEC)
        fp.write('ARRL-SECTION: %s\n' % self.MY_SEC)
        fp.write('GRID-LOCATOR: %s\n' % self.MY_GRID)
                    
    # Scoring routine for ARRL VHF contest for a single qso
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE,HIST2):
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
            
        self.Qs.append([call,grid,dx_km,qso_points])
            
        self.nqsos+=1
        if not dupe:
            self.total_km += dx_km
            self.nqsos2 += 1;
            self.total_points += qso_points

            self.NQSOS[band] +=1
            idx2 = self.BANDS.index(band)
            self.band_cnt[idx2] += 1
            self.dxccs.append(dx_station.country)

            # Info for multi-qsos
            exch_in=grid
            if call in self.EXCHANGES.keys():
                self.EXCHANGES[call].append(exch_in)
            else:
                self.EXCHANGES[call]=[exch_in]
            
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

        for Q in self.Qs:
            print(Q)

        dxccs=list(set(self.dxccs)) 
        dxccs.sort()
        print('\nNo. unique DXCCs =',len(dxccs))
        print(dxccs)
        
        avg_dx_km = self.total_km / self.nqsos2
        print('\nLongest DX:',self.max_km,'km')
        print(self.longest)
        print('\nAverage DX:',avg_dx_km,'km')
        
        #print 'GRID FIELDS:',sc.grid_fields
        print('\nBand\t# QSOs\t# Fields\tGrid Fields')
        mults=0
        for i in range(len(self.BANDS)):
            b=self.BANDS[i]
            fields = list( self.grid_fields[b] )
            fields.sort()
            print(b,'\t',self.band_cnt[i],'\t',len(fields),'\t',fields)
            mults+=len(fields)

        print('Totals:\t',self.nqsos,'\t',mults)

        print('\nNo. QSOs      =',self.nqsos)
        print('No. Uniques   =',self.nqsos2)
        #print('Band Count      =',self.band_cnt,'  =  ',int(sum(self.band_cnt)))
        print('QSO points    =',self.total_points)
        print('Multipliers   =',mults)
        print('Claimed Score =',self.total_points*mults)

